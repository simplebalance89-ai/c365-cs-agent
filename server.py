"""
server.py — C365 CS Agent: FastAPI main application.

Routes:
  GET  /                     → API info
  GET  /health               → Health check (services connectivity)
  GET  /demo                 → Interactive demo dashboard (HTML)
  GET  /api/demo             → Demo data as JSON (mock or live AI)

  GET  /tickets              → List Zendesk tickets
  GET  /tickets/{id}         → Get single ticket
  GET  /tickets/search       → Search tickets
  POST /tickets/{id}/classify   → AI classify a ticket
  POST /tickets/{id}/respond    → AI generate response; optionally post to Zendesk
  POST /tickets/{id}/update     → Update ticket status/comment

  GET  /emails/unread        → List unread emails from monitored mailbox
  GET  /emails/{id}          → Get single email
  POST /emails/{id}/process  → Parse email, classify, draft response
  POST /emails/{id}/send     → Send a drafted response

  GET  /customers/{email}/history  → AI summary of customer ticket history
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import ai_engine
import outlook_client
import zendesk_client
from config import get_settings
from models import (
    ClassifyRequest,
    CustomerHistorySummary,
    DemoResponse,
    HealthResponse,
    InboundEmail,
    OutboundEmail,
    ProcessEmailRequest,
    RespondRequest,
    SentimentLabel,
    SuggestedResponse,
    TicketCategory,
    TicketClassification,
    TicketPriority,
    TicketStatus,
    ZendeskComment,
    ZendeskTicket,
    ZendeskTicketUpdateRequest,
)

# ── App setup ─────────────────────────────────────────────────────────────────

settings = get_settings()

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="C365 CS Agent",
    description="AI-powered customer service agent for C365 — Zendesk + Outlook + Claude",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Root ──────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Info"])
def root() -> dict[str, Any]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs",
        "demo": "/demo",
        "health": "/health",
    }


# ── Health Check ──────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["Info"])
def health_check() -> HealthResponse:
    """
    Check connectivity to all external services.
    Returns 200 with per-service status. Does not raise on partial failure.
    """
    zendesk_ok = zendesk_client.check_connection()
    graph_ok = outlook_client.check_connection()

    # Claude health: just verify key is set (avoid burning tokens on health checks)
    claude_ok = bool(settings.anthropic_api_key)

    return HealthResponse(
        status="ok" if all([zendesk_ok, graph_ok, claude_ok]) else "degraded",
        version=settings.app_version,
        environment=settings.environment,
        services={
            "zendesk": "ok" if zendesk_ok else "unavailable",
            "microsoft_graph": "ok" if graph_ok else "unavailable",
            "claude_ai": "ok" if claude_ok else "no_api_key",
        },
    )


# ── DEMO ENDPOINT ─────────────────────────────────────────────────────────────

@app.get("/demo", response_model=DemoResponse, tags=["Demo"])
def demo() -> DemoResponse:
    """Serve the interactive demo dashboard."""
    static_dir = Path(__file__).parent / "static"
    return FileResponse(static_dir / "index.html")


@app.get("/api/demo", response_model=DemoResponse, tags=["Demo"])
def demo_api() -> DemoResponse:
    """
    JSON API for demo data. Uses real Claude AI with mock ticket/email data.
    No Zendesk or Graph credentials required.
    """
    # Mock ticket: a frustrated client with a billing dispute
    mock_ticket = ZendeskTicket(
        id=10042,
        subject="Incorrect charge on my November invoice — $850 over what I agreed",
        description=(
            "Hi,\n\n"
            "I just received my November invoice and there's a charge of $2,350 "
            "but my agreement clearly states $1,500/month for our ERP support engagement. "
            "This is the SECOND time this has happened. I'm extremely frustrated. "
            "If this isn't resolved by end of week, I'll be looking at other options. "
            "I have a signed service agreement I can forward.\n\n"
            "— Marcus Chen\n"
            "  TechVentures Inc.\n"
            "  marcus.chen@techventures.io"
        ),
        status=TicketStatus.open,
        priority=TicketPriority.normal,
        requester_id=88201,
        tags=["billing", "overcharge"],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    # Mock inbound email
    mock_email = InboundEmail(
        message_id="demo-msg-001",
        subject="ERP integration inquiry — P21 to Salesforce",
        sender_name="Sarah Park",
        sender_email="s.park@designstudio.co",
        body_text=(
            "Hi,\n\n"
            "We're evaluating ERP consulting partners for a P21 to Salesforce integration. "
            "Do you offer a discovery session before scoping the project? Also, do you "
            "have experience with automated data syncs between the two platforms?\n\n"
            "Thanks,\nSarah"
        ),
        received_at=datetime.now(timezone.utc),
    )

    # Try real AI, fall back to mock results
    try:
        classification = ai_engine.classify_ticket(mock_ticket)
        suggested_response = ai_engine.generate_ticket_response(
            ticket=mock_ticket,
            classification=classification,
            requester_name="Marcus",
        )
        email_classification = ai_engine.classify_ticket(
            ZendeskTicket(id=0, subject=mock_email.subject, description=mock_email.body_text, status=TicketStatus.new)
        )
        email_draft = ai_engine.generate_email_response(mock_email, email_classification)
        demo_msg = "Live demo running. Classification and responses generated by Claude AI in real-time using C365 knowledge base."
    except Exception as exc:
        logger.warning("AI unavailable for demo, using mock results: %s", exc)
        classification = TicketClassification(
            ticket_id=mock_ticket.id,
            priority=TicketPriority.high,
            category=TicketCategory.billing,
            sentiment=SentimentLabel.frustrated,
            confidence=0.95,
            summary="Client reports being overcharged $850 on November invoice. Second occurrence. Threatening to leave.",
            should_escalate=True,
            escalation_reason="Repeat billing error with flight risk language",
        )
        suggested_response = SuggestedResponse(
            ticket_id=mock_ticket.id,
            subject="Re: Incorrect charge on my November invoice",
            body="Hi Marcus,\n\nThank you for bringing this to our attention. I sincerely apologize for the billing discrepancy — this should not have happened, especially a second time. I've flagged your account for immediate review and our billing team will issue a credit for the $850 overcharge within 24 hours. I'll personally follow up to ensure this is resolved and it doesn't happen again.\n\nBest regards,\nC365 Support",
            suggested_status=TicketStatus.pending,
        )
        email_draft = SuggestedResponse(
            subject="Re: ERP integration inquiry — P21 to Salesforce",
            body="Hi Sarah,\n\nThank you for reaching out! Yes, we absolutely offer a discovery session before scoping — it's actually how we start every engagement. We have deep experience with P21 to Salesforce integrations, including automated data syncs.\n\nWould you be available for a 30-minute discovery call this week?\n\nBest regards,\nC365 Support",
            suggested_status=TicketStatus.open,
        )
        demo_msg = "Demo running with mock AI results. Add ANTHROPIC_API_KEY for live Claude AI classification and responses."

    return DemoResponse(
        demo_ticket=mock_ticket,
        classification=classification,
        suggested_response=suggested_response,
        demo_email=mock_email,
        email_draft=email_draft,
        message=demo_msg,
    )


# ── Zendesk: Ticket Routes ────────────────────────────────────────────────────

@app.get("/tickets", tags=["Tickets"])
def list_tickets(
    status: str = Query("open", description="Zendesk ticket status filter"),
    per_page: int = Query(25, le=100),
    page: int = Query(1, ge=1),
) -> list[ZendeskTicket]:
    """List Zendesk tickets filtered by status."""
    try:
        return zendesk_client.list_tickets(status=status, per_page=per_page, page=page)
    except Exception as exc:
        logger.error("list_tickets failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Zendesk error: {exc}")


@app.get("/tickets/search", tags=["Tickets"])
def search_tickets(
    q: str = Query(..., description="Zendesk search query (appended to type:ticket)"),
    per_page: int = Query(25, le=100),
) -> list[ZendeskTicket]:
    """Search tickets using Zendesk search syntax."""
    try:
        return zendesk_client.search_tickets(query=q, per_page=per_page)
    except Exception as exc:
        logger.error("search_tickets failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Zendesk error: {exc}")


@app.get("/tickets/{ticket_id}", tags=["Tickets"])
def get_ticket(ticket_id: int) -> ZendeskTicket:
    """Fetch a single Zendesk ticket."""
    try:
        return zendesk_client.get_ticket(ticket_id)
    except Exception as exc:
        logger.error("get_ticket %d failed: %s", ticket_id, exc)
        raise HTTPException(status_code=502, detail=f"Zendesk error: {exc}")


@app.post("/tickets/{ticket_id}/classify", tags=["Tickets", "AI"])
def classify_ticket(ticket_id: int) -> TicketClassification:
    """AI-classify a ticket: priority, category, sentiment, escalation flag."""
    try:
        ticket = zendesk_client.get_ticket(ticket_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Zendesk error: {exc}")

    return ai_engine.classify_ticket(ticket)


@app.post("/tickets/{ticket_id}/respond", tags=["Tickets", "AI"])
def respond_to_ticket(ticket_id: int, body: RespondRequest) -> SuggestedResponse:
    """
    Generate an AI response for a ticket.
    If auto_send=True, the response is posted as a public comment in Zendesk.
    """
    try:
        ticket = zendesk_client.get_ticket(ticket_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Zendesk error fetching ticket: {exc}")

    # Fetch requester name if available
    requester_name: str | None = None
    if ticket.requester_id:
        try:
            user = zendesk_client.get_user(ticket.requester_id)
            requester_name = user.get("name", "").split()[0] if user.get("name") else None
        except Exception:
            pass

    classification = ai_engine.classify_ticket(ticket)
    response = ai_engine.generate_ticket_response(ticket, classification, requester_name)

    if body.auto_send:
        try:
            comment = ZendeskComment(
                ticket_id=ticket_id,
                body=response.body,
                public=True,
            )
            zendesk_client.add_comment(comment)

            if response.suggested_status:
                zendesk_client.update_ticket(ticket_id, status=response.suggested_status)

            logger.info("Auto-posted response to ticket %d", ticket_id)
        except Exception as exc:
            logger.error("Failed to post response to Zendesk: %s", exc)
            raise HTTPException(status_code=502, detail=f"Zendesk post failed: {exc}")

    return response


@app.put("/tickets/{ticket_id}/update", tags=["Tickets"])
def update_ticket(ticket_id: int, body: ZendeskTicketUpdateRequest) -> ZendeskTicket:
    """Update a ticket's status, priority, and/or add a comment."""
    try:
        if body.comment:
            comment = ZendeskComment(
                ticket_id=ticket_id,
                body=body.comment,
                public=body.public_comment,
            )
            zendesk_client.add_comment(comment)

        updated = zendesk_client.update_ticket(
            ticket_id,
            status=body.status,
            priority=body.priority,
            tags_add=body.tags,
        )
        return updated
    except Exception as exc:
        logger.error("update_ticket %d failed: %s", ticket_id, exc)
        raise HTTPException(status_code=502, detail=f"Zendesk error: {exc}")


# ── Email / Outlook Routes ────────────────────────────────────────────────────

@app.get("/emails/unread", tags=["Email"])
def list_unread_emails(top: int = Query(20, le=50)) -> list[InboundEmail]:
    """List unread emails from the monitored Outlook mailbox."""
    try:
        return outlook_client.list_unread_emails(top=top)
    except Exception as exc:
        logger.error("list_unread_emails failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Graph API error: {exc}")


@app.get("/emails/{message_id}", tags=["Email"])
def get_email(message_id: str) -> InboundEmail:
    """Fetch a single email by Graph message ID."""
    try:
        return outlook_client.get_email(message_id)
    except Exception as exc:
        logger.error("get_email %s failed: %s", message_id, exc)
        raise HTTPException(status_code=502, detail=f"Graph API error: {exc}")


@app.post("/emails/{message_id}/process", tags=["Email", "AI"])
def process_email(message_id: str, body: ProcessEmailRequest) -> dict[str, Any]:
    """
    Process an inbound email:
    1. Fetch the email
    2. Check if a Zendesk ticket exists for the sender
    3. AI-classify and generate a draft response
    4. Optionally auto-reply (body.auto_reply=True)
    5. Mark email as read
    """
    try:
        email = outlook_client.get_email(message_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Graph API error: {exc}")

    # Classify the email
    mock_ticket = ZendeskTicket(
        id=0,
        subject=email.subject,
        description=email.body_text,
        status=TicketStatus.new,
    )
    classification = ai_engine.classify_ticket(mock_ticket)
    draft = ai_engine.generate_email_response(email, classification)

    # Attempt to find existing Zendesk ticket for this sender
    existing_ticket: ZendeskTicket | None = None
    try:
        results = zendesk_client.search_tickets(
            f'requester:"{email.sender_email}" status:open'
        )
        existing_ticket = results[0] if results else None
    except Exception:
        pass  # Non-fatal — we still have the AI draft

    result: dict[str, Any] = {
        "email": email,
        "classification": classification,
        "draft_response": draft,
        "existing_zendesk_ticket": existing_ticket,
        "auto_replied": False,
    }

    if body.auto_reply:
        try:
            outbound = OutboundEmail(
                to=[email.sender_email],
                subject=draft.subject,
                body_html=draft.body.replace("\n", "<br>"),
                reply_to_message_id=message_id,
            )
            outlook_client.send_email(outbound)
            outlook_client.mark_email_read(message_id)
            result["auto_replied"] = True
        except Exception as exc:
            logger.error("Auto-reply failed: %s", exc)
            result["auto_reply_error"] = str(exc)

    return result


@app.post("/emails/{message_id}/send", tags=["Email"])
def send_email_response(message_id: str, outbound: OutboundEmail) -> dict[str, str]:
    """Send a manually reviewed email response and mark original as read."""
    try:
        outlook_client.send_email(outbound)
        outlook_client.mark_email_read(message_id)
        return {"status": "sent", "to": ", ".join(outbound.to)}
    except Exception as exc:
        logger.error("send_email failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Graph API error: {exc}")


# ── Customer History ──────────────────────────────────────────────────────────

@app.get("/customers/{email}/history", tags=["Customers", "AI"])
def customer_history(email: str) -> CustomerHistorySummary:
    """Fetch all Zendesk tickets for a customer and return an AI-generated history summary."""
    try:
        user = zendesk_client.find_user_by_email(email)
        if not user:
            return CustomerHistorySummary(
                requester_email=email,
                total_tickets=0,
                open_tickets=0,
                avg_sentiment="neutral",
                top_categories=[],
                summary=f"No Zendesk user found for {email}.",
            )

        tickets = zendesk_client.get_tickets_by_requester(user["id"])
        return ai_engine.summarize_customer_history(email, tickets)
    except Exception as exc:
        logger.error("customer_history %s failed: %s", email, exc)
        raise HTTPException(status_code=502, detail=f"Error: {exc}")


# ── Static Files ─────────────────────────────────────────────────────────────

_static_dir = Path(__file__).parent / "static"
if _static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")


# ── Entry point for local dev ─────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )
