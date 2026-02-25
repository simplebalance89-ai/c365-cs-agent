"""
ai_engine.py — Claude-powered classification, response generation, and summarization.

All AI calls go through this module. Claude models are configured in config.py.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import anthropic

from config import get_settings
from knowledge_base import build_knowledge_context, SLA, CONTACTS
from models import (
    TicketCategory,
    TicketClassification,
    TicketPriority,
    TicketStatus,
    SentimentLabel,
    SuggestedResponse,
    CustomerHistorySummary,
    ZendeskTicket,
    InboundEmail,
)

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize Anthropic client — may be None if no API key
_client = None
if settings.anthropic_api_key:
    try:
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    except Exception:
        _client = None


# ── Internal helpers ──────────────────────────────────────────────────────────

def _call_claude(
    system: str,
    user: str,
    model: str | None = None,
    max_tokens: int | None = None,
) -> str:
    """Low-level Claude call. Returns raw text content."""
    if _client is None:
        raise RuntimeError("Anthropic API key not configured")
    model = model or settings.claude_model_respond
    max_tokens = max_tokens or settings.claude_max_tokens

    message = _client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": user}],
        system=system,
    )
    return message.content[0].text


def _parse_json_response(text: str) -> dict[str, Any]:
    """
    Extract JSON from Claude's response. Handles markdown code fences.
    Raises ValueError if no valid JSON found.
    """
    text = text.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(
            line for line in lines if not line.startswith("```")
        ).strip()

    # Find outermost JSON object
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON object found in response: {text[:200]}")

    return json.loads(text[start:end])


# ── Ticket Classification ─────────────────────────────────────────────────────

CLASSIFY_SYSTEM = """
You are an expert customer service operations analyst for Conveyance365,
an ERP consulting and AI automation company.

Your job is to classify incoming support tickets. You must respond with ONLY
a valid JSON object — no commentary, no markdown, just JSON.

Classification schema:
{
  "category": one of [billing, access, maintenance, booking, lease, amenities, general, escalation],
  "priority": one of [urgent, high, normal, low],
  "sentiment": one of [positive, neutral, frustrated, angry],
  "should_escalate": boolean,
  "escalation_reason": string or null,
  "confidence": float between 0.0 and 1.0,
  "summary": "1-2 sentence plain-English summary of the issue"
}

Priority guidelines:
- urgent: System outage, data loss risk, legal threat, client threatening to cancel, production ERP down
- high: Billing dispute, integration failure, repeated issue, urgent support request
- normal: Routine requests, general questions, minor issues
- low: Suggestions, compliments, non-time-sensitive inquiries

Escalation triggers (set should_escalate=true):
- Legal language or threats
- Production system outage or data integrity risk
- Client threatening to cancel or mentioning competitors
- Media/PR mention
- Second complaint on same issue
- Billing dispute over $500
- Critical ERP or integration failure
"""


def classify_ticket(ticket: ZendeskTicket) -> TicketClassification:
    """Classify a Zendesk ticket using Claude."""
    knowledge = build_knowledge_context()

    user_prompt = f"""
Classify this Conveyance365 support ticket.

TICKET ID: {ticket.id}
SUBJECT: {ticket.subject}
DESCRIPTION:
{ticket.description or "(no description provided)"}

EXISTING PRIORITY: {ticket.priority}
EXISTING STATUS: {ticket.status}
TAGS: {", ".join(ticket.tags) if ticket.tags else "none"}

KNOWLEDGE BASE CONTEXT:
{knowledge}
"""

    raw = _call_claude(
        system=CLASSIFY_SYSTEM,
        user=user_prompt,
        model=settings.claude_model_classify,
    )

    try:
        data = _parse_json_response(raw)
        return TicketClassification(
            ticket_id=ticket.id,
            category=TicketCategory(data["category"]),
            priority=TicketPriority(data["priority"]),
            sentiment=SentimentLabel(data["sentiment"]),
            should_escalate=bool(data["should_escalate"]),
            escalation_reason=data.get("escalation_reason"),
            confidence=float(data.get("confidence", 0.85)),
            summary=data["summary"],
        )
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        logger.error("Failed to parse classification response: %s | raw: %s", exc, raw[:300])
        # Safe fallback
        return TicketClassification(
            ticket_id=ticket.id,
            category=TicketCategory.general,
            priority=TicketPriority.normal,
            sentiment=SentimentLabel.neutral,
            should_escalate=False,
            confidence=0.0,
            summary="Classification failed — manual review required.",
        )


# ── Response Generation ───────────────────────────────────────────────────────

RESPOND_SYSTEM = """
You are a customer service agent for Conveyance365, a premium commercial
office solutions company. You write professional, warm, solution-oriented
responses to client inquiries.

Respond ONLY with a valid JSON object:
{
  "subject": "Re: <original subject>",
  "body": "Full email/comment body in plain text. Use \\n for line breaks.",
  "suggested_status": one of [open, pending, solved],
  "suggested_tags": ["tag1", "tag2"],
  "internal_notes": "Optional notes for the agent — not sent to customer. Can be null."
}

Response guidelines:
- Start with a greeting using the requester's first name if available
- Acknowledge the issue/request with empathy
- Provide a clear, actionable answer
- End with a specific next step or offer to help further
- Sign off with "The Conveyance365 Team" unless writing as a named agent
- Keep body under 250 words unless complexity demands more
- Never make up prices, timelines, or specific project details — direct to the right contact instead
- If escalation is needed, acknowledge and say you're connecting them with the right person
"""


def generate_ticket_response(
    ticket: ZendeskTicket,
    classification: TicketClassification,
    requester_name: str | None = None,
) -> SuggestedResponse:
    """Generate a suggested response for a Zendesk ticket."""
    knowledge = build_knowledge_context(
        categories=[classification.category.value] if classification.category else None
    )

    user_prompt = f"""
Generate a customer service response for this Conveyance365 support ticket.

TICKET ID: {ticket.id}
SUBJECT: {ticket.subject}
FROM: {requester_name or "Member"}
DESCRIPTION:
{ticket.description or "(no description provided)"}

CLASSIFICATION:
- Category: {classification.category.value}
- Priority: {classification.priority.value}
- Sentiment: {classification.sentiment.value}
- Should Escalate: {classification.should_escalate}
- Summary: {classification.summary}

ESCALATION CONTACT (if needed): {CONTACTS["escalation"]}

KNOWLEDGE BASE:
{knowledge}

Write a response that directly addresses the client's issue.
{"IMPORTANT: This ticket should be escalated. Acknowledge the urgency and let the client know you are connecting them with a senior team member." if classification.should_escalate else ""}
"""

    raw = _call_claude(system=RESPOND_SYSTEM, user=user_prompt)

    try:
        data = _parse_json_response(raw)
        return SuggestedResponse(
            ticket_id=ticket.id,
            subject=data["subject"],
            body=data["body"],
            suggested_status=TicketStatus(data.get("suggested_status", "pending")),
            suggested_tags=data.get("suggested_tags", []),
            internal_notes=data.get("internal_notes"),
        )
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        logger.error("Failed to parse response generation: %s | raw: %s", exc, raw[:300])
        return SuggestedResponse(
            ticket_id=ticket.id,
            subject=f"Re: {ticket.subject}",
            body=(
                f"Dear {requester_name or 'Member'},\n\n"
                "Thank you for reaching out to Conveyance365. We have received your message "
                "and a member of our team will be in touch shortly.\n\n"
                "The Conveyance365 Team"
            ),
            suggested_status=TicketStatus.pending,
        )


# ── Email Response Generation ─────────────────────────────────────────────────

def generate_email_response(
    email: InboundEmail,
    classification: TicketClassification | None = None,
) -> SuggestedResponse:
    """Generate a draft response for an inbound customer email."""
    knowledge = build_knowledge_context(
        categories=[classification.category.value] if classification else None
    )

    user_prompt = f"""
Generate a customer service email response for this inbound message to Conveyance365.

FROM: {email.sender_name or email.sender_email}
SUBJECT: {email.subject}
MESSAGE:
{email.body_text}

{"CLASSIFICATION: " + classification.model_dump_json() if classification else ""}

KNOWLEDGE BASE:
{knowledge}

Write a warm, professional email response addressing the inquiry directly.
"""

    raw = _call_claude(system=RESPOND_SYSTEM, user=user_prompt)

    try:
        data = _parse_json_response(raw)
        return SuggestedResponse(
            subject=data["subject"],
            body=data["body"],
            suggested_status=TicketStatus(data.get("suggested_status", "pending")),
            suggested_tags=data.get("suggested_tags", []),
            internal_notes=data.get("internal_notes"),
        )
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        logger.error("Failed to parse email response: %s | raw: %s", exc, raw[:300])
        return SuggestedResponse(
            subject=f"Re: {email.subject}",
            body=(
                f"Dear {email.sender_name or 'Member'},\n\n"
                "Thank you for contacting Conveyance365. We have received your message "
                "and will respond within 4 business hours.\n\n"
                "The Conveyance365 Team"
            ),
            suggested_status=TicketStatus.pending,
        )


# ── Customer History Summarization ───────────────────────────────────────────

HISTORY_SYSTEM = """
You are a customer success analyst for Conveyance365. Given a list of support
tickets for a client, produce a concise client profile summary.

Respond ONLY with a valid JSON object:
{
  "summary": "3-4 sentence narrative summary of the client's history and current standing",
  "avg_sentiment": "positive | neutral | frustrated | angry",
  "top_categories": ["category1", "category2"],
  "vip_flag": boolean
}

Flag as VIP if:
- Client has been with C365 for many tickets over time with positive sentiment
- Client has a high volume of tickets (>10) suggesting enterprise-level engagement
- Client explicitly mentioned in escalation history but issue was resolved positively
"""


def summarize_customer_history(
    requester_email: str,
    tickets: list[ZendeskTicket],
) -> CustomerHistorySummary:
    """Produce an AI summary of a customer's ticket history."""
    if not tickets:
        return CustomerHistorySummary(
            requester_email=requester_email,
            total_tickets=0,
            open_tickets=0,
            avg_sentiment="neutral",
            top_categories=[],
            summary="No ticket history found for this client.",
        )

    open_count = sum(
        1 for t in tickets
        if t.status in (TicketStatus.new, TicketStatus.open, TicketStatus.pending)
    )

    ticket_summaries = "\n".join(
        f"- [{t.id}] {t.subject} | status={t.status.value} | priority={t.priority or 'none'}"
        for t in tickets[:30]  # cap to avoid token overflow
    )

    user_prompt = f"""
Summarize the ticket history for this Conveyance365 client.

EMAIL: {requester_email}
TOTAL TICKETS: {len(tickets)}
OPEN TICKETS: {open_count}

TICKET LIST:
{ticket_summaries}

Provide an honest assessment of their experience and flag if they should be treated as VIP.
"""

    raw = _call_claude(system=HISTORY_SYSTEM, user=user_prompt)

    try:
        data = _parse_json_response(raw)
        return CustomerHistorySummary(
            requester_email=requester_email,
            total_tickets=len(tickets),
            open_tickets=open_count,
            avg_sentiment=data.get("avg_sentiment", "neutral"),
            top_categories=data.get("top_categories", []),
            summary=data["summary"],
            vip_flag=bool(data.get("vip_flag", False)),
        )
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        logger.error("Failed to parse history summary: %s | raw: %s", exc, raw[:300])
        return CustomerHistorySummary(
            requester_email=requester_email,
            total_tickets=len(tickets),
            open_tickets=open_count,
            avg_sentiment="neutral",
            top_categories=[],
            summary="Summary generation failed — manual review of ticket history recommended.",
        )
