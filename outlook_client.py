"""
outlook_client.py — Microsoft Graph API wrapper for C365 Outlook/Exchange email.

Uses MSAL (Microsoft Authentication Library) with client credentials flow
(app-only auth, no user sign-in required). Requires:
  - ms_tenant_id
  - ms_client_id
  - ms_client_secret
  - ms_mailbox (the shared/support mailbox UPN)

Docs: https://learn.microsoft.com/en-us/graph/api/resources/mail-api-overview

Set DEMO_MODE = True to bypass the real Graph API and return realistic mock data.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta, timezone
from html import unescape
from typing import Any

import httpx
import msal

from config import get_settings
from models import InboundEmail, OutboundEmail

logger = logging.getLogger(__name__)
settings = get_settings()

GRAPH_BASE = "https://graph.microsoft.com/v1.0"

# ── Demo Mode Toggle ─────────────────────────────────────────────────────────
DEMO_MODE = True


# ── Mock Data ────────────────────────────────────────────────────────────────

def _demo_now() -> datetime:
    return datetime.now(timezone.utc)


def _demo_emails() -> list[InboundEmail]:
    """Return a fixed set of realistic demo emails."""
    now = _demo_now()
    return [
        InboundEmail(
            message_id="MSG-DEMO-001",
            subject="RE: P21 Inventory Valuation report timeout",
            sender_name="Maria Gonzalez",
            sender_email="maria.gonzalez@acmedist.com",
            body_text=(
                "Hi team,\n\n"
                "Following up on ticket #40112. The report is still timing out "
                "after the server patch. We tried increasing the SQL timeout to "
                "600 seconds but no change. Month-end close is Friday.\n\n"
                "Can we get a call scheduled today?\n\n"
                "Thanks,\nMaria"
            ),
            received_at=now - timedelta(hours=2),
            thread_id="THREAD-DEMO-001",
        ),
        InboundEmail(
            message_id="MSG-DEMO-002",
            subject="EDI 856 ASN sync — still down",
            sender_name="James Whitfield",
            sender_email="j.whitfield@northstarlogistics.com",
            body_text=(
                "Support,\n\n"
                "This is day 4 of the EDI 856 sync failure. We now have 22 "
                "shipments that haven't posted to P21. Our warehouse team is "
                "doing manual entry which is error-prone and slow.\n\n"
                "The middleware log shows:\n"
                "  ERROR 401 Unauthorized — POST /api/v1/edi/inbound\n"
                "  Token refresh failed: invalid_client\n\n"
                "We regenerated the client secret yesterday but same result. "
                "Is there a cached token somewhere that needs to be cleared?\n\n"
                "James Whitfield\nNorthStar Logistics"
            ),
            received_at=now - timedelta(hours=5),
            thread_id="THREAD-DEMO-002",
        ),
        InboundEmail(
            message_id="MSG-DEMO-003",
            subject="Question about AI agent auto-classification setup",
            sender_name="Priya Sharma",
            sender_email="priya@tektonparts.com",
            body_text=(
                "Hello,\n\n"
                "We're on the Professional plan and want to enable the AI "
                "auto-classification feature. The settings tab appears greyed "
                "out in our admin panel. Is there an additional license needed "
                "or a feature flag we need to request?\n\n"
                "Appreciate the help.\n\n"
                "Best,\nPriya Sharma\nTekton Parts Inc."
            ),
            received_at=now - timedelta(hours=12),
            thread_id="THREAD-DEMO-003",
        ),
        InboundEmail(
            message_id="MSG-DEMO-004",
            subject="Invoice mismatch — PO 7892 vs INV-2026-0412",
            sender_name="Robert Chen",
            sender_email="rchen@precisionmfg.com",
            body_text=(
                "Hi Billing,\n\n"
                "PO 7892 was for 480 units at $12.50/unit ($6,000 total). "
                "Invoice INV-2026-0412 shows 480 units at $13.75/unit ($6,600). "
                "That's a $600 discrepancy.\n\n"
                "I've attached a screenshot of both documents. Please issue a "
                "credit memo or revised invoice ASAP so we can process payment.\n\n"
                "Robert Chen\nPrecision Manufacturing"
            ),
            received_at=now - timedelta(days=1),
            thread_id="THREAD-DEMO-004",
        ),
        InboundEmail(
            message_id="MSG-DEMO-005",
            subject="RE: Data migration — go-live timeline check",
            sender_name="Angela Torres",
            sender_email="angela.torres@summitsupply.com",
            body_text=(
                "Peter,\n\n"
                "Just checking in on the migration status. Our go-live target "
                "is March 15 and we haven't received an update in two weeks. "
                "Can you share:\n"
                "  1. Current migration completion percentage\n"
                "  2. Any blockers\n"
                "  3. Revised timeline if needed\n\n"
                "We have a board meeting March 10 and need to report status.\n\n"
                "Thanks,\nAngela Torres\nSummit Supply Co."
            ),
            received_at=now - timedelta(days=2),
            thread_id="THREAD-DEMO-005",
        ),
        InboundEmail(
            message_id="MSG-DEMO-006",
            subject="New user provisioning request — 3 users",
            sender_name="Kevin Draper",
            sender_email="kdraper@greatlakesind.com",
            body_text=(
                "Hi Support,\n\n"
                "We need three new users provisioned in the C365 portal:\n\n"
                "  1. Sarah Mitchell — sarah.m@greatlakesind.com — Warehouse role\n"
                "  2. Tom Alvarez — tom.a@greatlakesind.com — Purchasing role\n"
                "  3. Diana Reyes — diana.r@greatlakesind.com — Admin role\n\n"
                "All three should have SSO enabled via our Azure AD tenant.\n\n"
                "Thanks,\nKevin Draper\nGreat Lakes Industries"
            ),
            received_at=now - timedelta(days=3),
            thread_id="THREAD-DEMO-006",
        ),
        InboundEmail(
            message_id="MSG-DEMO-007",
            subject="RE: Warehouse label printer issue — resolved",
            sender_name="Kevin Draper",
            sender_email="kdraper@greatlakesind.com",
            body_text=(
                "Hey team,\n\n"
                "Just wanted to confirm the label printer issue on Pick Station 3 "
                "is resolved. The fix from your Tier 2 team (updating the ODBC "
                "driver) worked. All three stations printing correctly now.\n\n"
                "Thanks for the quick turnaround.\n\n"
                "Kevin"
            ),
            received_at=now - timedelta(days=10),
            thread_id="THREAD-DEMO-007",
        ),
    ]


_DEMO_THREAD_MESSAGES: dict[str, list[InboundEmail]] = {}


def _build_demo_threads() -> dict[str, list[InboundEmail]]:
    """Build thread lookup from demo emails (lazy init)."""
    if not _DEMO_THREAD_MESSAGES:
        for email in _demo_emails():
            if email.thread_id:
                _DEMO_THREAD_MESSAGES.setdefault(email.thread_id, []).append(email)
    return _DEMO_THREAD_MESSAGES


# ── Token Acquisition ─────────────────────────────────────────────────────────

_token_cache: dict[str, str] = {}


def _get_access_token() -> str:
    """
    Acquire a Graph API token using client credentials (app-only).
    Tokens are cached in-process; MSAL handles refresh.
    """
    app = msal.ConfidentialClientApplication(
        client_id=settings.ms_client_id,
        client_credential=settings.ms_client_secret,
        authority=f"https://login.microsoftonline.com/{settings.ms_tenant_id}",
    )

    result = app.acquire_token_for_client(scopes=[settings.ms_graph_scope])

    if "access_token" not in result:
        error = result.get("error_description", result.get("error", "Unknown MSAL error"))
        raise RuntimeError(f"Failed to acquire Graph token: {error}")

    return result["access_token"]


def _get_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_get_access_token()}",
        "Content-Type": "application/json",
    }


def _get_client() -> httpx.Client:
    return httpx.Client(
        base_url=GRAPH_BASE,
        headers=_get_headers(),
        timeout=30.0,
    )


# ── HTML -> Plain Text ───────────────────────────────────────────────────────

def _html_to_text(html: str) -> str:
    """Very lightweight HTML-to-text conversion for email bodies."""
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"<p[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)  # strip remaining tags
    text = unescape(text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


# ── Parse Graph Message -> InboundEmail ──────────────────────────────────────

def _parse_message(msg: dict[str, Any]) -> InboundEmail:
    sender_info = msg.get("from", {}).get("emailAddress", {})
    body = msg.get("body", {})

    body_html = body.get("content", "")
    if body.get("contentType", "").lower() == "html":
        body_text = _html_to_text(body_html)
    else:
        body_text = body_html
        body_html = None

    return InboundEmail(
        message_id=msg["id"],
        subject=msg.get("subject") or "(no subject)",
        sender_name=sender_info.get("name"),
        sender_email=sender_info.get("address", ""),
        body_text=body_text,
        body_html=body_html if body.get("contentType", "").lower() == "html" else None,
        received_at=msg.get("receivedDateTime"),
        thread_id=msg.get("conversationId"),
    )


# ── Read Operations ───────────────────────────────────────────────────────────

def list_unread_emails(
    mailbox: str | None = None,
    folder: str = "Inbox",
    top: int = 20,
) -> list[InboundEmail]:
    """
    Fetch unread messages from the monitored mailbox.
    mailbox defaults to settings.ms_mailbox.
    """
    if DEMO_MODE:
        return _demo_emails()[:top]

    mailbox = mailbox or settings.ms_mailbox

    with _get_client() as client:
        response = client.get(
            f"/users/{mailbox}/mailFolders/{folder}/messages",
            params={
                "$filter": "isRead eq false",
                "$top": top,
                "$orderby": "receivedDateTime desc",
                "$select": (
                    "id,subject,from,body,receivedDateTime,conversationId,isRead"
                ),
            },
        )
        response.raise_for_status()
        messages = response.json().get("value", [])
        return [_parse_message(m) for m in messages]


def get_email(
    message_id: str,
    mailbox: str | None = None,
) -> InboundEmail:
    """Fetch a single email by message ID."""
    if DEMO_MODE:
        for email in _demo_emails():
            if email.message_id == message_id:
                return email
        raise ValueError(f"Demo email {message_id} not found")

    mailbox = mailbox or settings.ms_mailbox

    with _get_client() as client:
        response = client.get(
            f"/users/{mailbox}/messages/{message_id}",
            params={"$select": "id,subject,from,body,receivedDateTime,conversationId"},
        )
        response.raise_for_status()
        return _parse_message(response.json())


def get_thread_messages(
    conversation_id: str,
    mailbox: str | None = None,
    top: int = 10,
) -> list[InboundEmail]:
    """Fetch all messages in a conversation thread."""
    if DEMO_MODE:
        threads = _build_demo_threads()
        return threads.get(conversation_id, [])[:top]

    mailbox = mailbox or settings.ms_mailbox

    with _get_client() as client:
        response = client.get(
            f"/users/{mailbox}/messages",
            params={
                "$filter": f"conversationId eq '{conversation_id}'",
                "$top": top,
                "$orderby": "receivedDateTime asc",
                "$select": "id,subject,from,body,receivedDateTime,conversationId",
            },
        )
        response.raise_for_status()
        return [_parse_message(m) for m in response.json().get("value", [])]


# ── Write Operations ──────────────────────────────────────────────────────────

def send_email(
    email: OutboundEmail,
    mailbox: str | None = None,
) -> bool:
    """
    Send an email from the monitored mailbox.
    Returns True on success.
    """
    if DEMO_MODE:
        logger.info(
            "[DEMO] Email sent to %s — Subject: %s",
            ", ".join(email.to),
            email.subject,
        )
        return True

    mailbox = mailbox or settings.ms_mailbox

    payload = {
        "message": {
            "subject": email.subject,
            "body": {
                "contentType": "HTML",
                "content": email.body_html,
            },
            "toRecipients": [
                {"emailAddress": {"address": addr}} for addr in email.to
            ],
        },
        "saveToSentItems": True,
    }

    # Thread reply — attach to original conversation
    if email.reply_to_message_id:
        with _get_client() as client:
            response = client.post(
                f"/users/{mailbox}/messages/{email.reply_to_message_id}/reply",
                json={"message": payload["message"]},
            )
            response.raise_for_status()
            return True

    with _get_client() as client:
        response = client.post(
            f"/users/{mailbox}/sendMail",
            json=payload,
        )
        response.raise_for_status()
        return True


def mark_email_read(
    message_id: str,
    mailbox: str | None = None,
) -> bool:
    """Mark a message as read after processing."""
    if DEMO_MODE:
        logger.info("[DEMO] Marked email %s as read", message_id)
        return True

    mailbox = mailbox or settings.ms_mailbox

    with _get_client() as client:
        response = client.patch(
            f"/users/{mailbox}/messages/{message_id}",
            json={"isRead": True},
        )
        response.raise_for_status()
        return True


def create_draft(
    email: OutboundEmail,
    mailbox: str | None = None,
) -> dict[str, Any]:
    """
    Create a draft reply (does not send). Useful for human-in-the-loop review
    before sending AI-generated responses.
    """
    if DEMO_MODE:
        logger.info(
            "[DEMO] Draft created for %s — Subject: %s",
            ", ".join(email.to),
            email.subject,
        )
        return {
            "id": "DRAFT-DEMO-001",
            "subject": email.subject,
            "body": {"contentType": "HTML", "content": email.body_html},
            "toRecipients": [{"emailAddress": {"address": addr}} for addr in email.to],
            "isDraft": True,
        }

    mailbox = mailbox or settings.ms_mailbox

    payload = {
        "subject": email.subject,
        "body": {
            "contentType": "HTML",
            "content": email.body_html,
        },
        "toRecipients": [
            {"emailAddress": {"address": addr}} for addr in email.to
        ],
    }

    with _get_client() as client:
        response = client.post(
            f"/users/{mailbox}/messages",
            json=payload,
        )
        response.raise_for_status()
        return response.json()


# ── Health Check ──────────────────────────────────────────────────────────────

def check_connection() -> bool:
    """Verify Graph API access. Returns True on success."""
    if DEMO_MODE:
        logger.info("[DEMO] Outlook health check — simulated OK")
        return True

    try:
        with _get_client() as client:
            response = client.get(
                f"/users/{settings.ms_mailbox}",
                params={"$select": "id,mail"},
            )
            return response.status_code == 200
    except Exception as exc:
        logger.warning("Graph API health check failed: %s", exc)
        return False
