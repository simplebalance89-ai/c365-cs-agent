"""
zendesk_client.py — Zendesk API wrapper for Luxor Workspaces Customer Service Agent.

Authentication: email/token (Basic Auth with "{email}/token:{api_token}").
Docs: https://developer.zendesk.com/api-reference/

Set DEMO_MODE = True to bypass the real Zendesk API and return realistic mock data.
"""

from __future__ import annotations

import base64
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from config import get_settings
from models import (
    TicketPriority,
    TicketStatus,
    ZendeskComment,
    ZendeskTicket,
)

logger = logging.getLogger(__name__)
settings = get_settings()

# ── Demo Mode Toggle ─────────────────────────────────────────────────────────
DEMO_MODE = True


# ── Mock Data ────────────────────────────────────────────────────────────────

def _demo_now() -> datetime:
    return datetime.now(timezone.utc)


def _demo_tickets() -> list[ZendeskTicket]:
    """Return a fixed set of realistic demo tickets."""
    now = _demo_now()
    return [
        ZendeskTicket(
            id=40112,
            subject="P21 report not generating",
            description=(
                "We're trying to run the Inventory Valuation report in P21 "
                "and it hangs at 80% then times out. Started happening after "
                "last weekend's server patch. Urgent — month-end close depends on this."
            ),
            status=TicketStatus.open,
            priority=TicketPriority.urgent,
            requester_id=9001,
            assignee_id=5001,
            tags=["p21", "reporting", "month-end"],
            created_at=now - timedelta(hours=6),
            updated_at=now - timedelta(hours=2),
        ),
        ZendeskTicket(
            id=40098,
            subject="Integration sync failing — EDI 856 ASN",
            description=(
                "Our EDI 856 ASN documents are not syncing to P21 since Tuesday. "
                "The middleware log shows a 401 from the API gateway. We re-entered "
                "the credentials but it keeps failing. 14 shipments stuck."
            ),
            status=TicketStatus.open,
            priority=TicketPriority.high,
            requester_id=9002,
            assignee_id=5001,
            tags=["edi", "integration", "p21", "edi-856"],
            created_at=now - timedelta(days=3),
            updated_at=now - timedelta(hours=8),
        ),
        ZendeskTicket(
            id=40087,
            subject="Need help with AI agent configuration",
            description=(
                "We want to enable the auto-classification feature on our CS agent "
                "but the 'AI Settings' tab is greyed out. We are on the Professional "
                "plan. Can someone walk us through the setup?"
            ),
            status=TicketStatus.pending,
            priority=TicketPriority.normal,
            requester_id=9003,
            assignee_id=5002,
            tags=["ai-agent", "configuration", "onboarding"],
            created_at=now - timedelta(days=5),
            updated_at=now - timedelta(days=1),
        ),
        ZendeskTicket(
            id=40071,
            subject="Invoice discrepancy Q4 — PO 7892",
            description=(
                "Invoice #INV-2026-0412 doesn't match PO 7892. The PO shows "
                "480 units at $12.50 but the invoice billed 480 units at $13.75. "
                "Difference is $600. Need a revised invoice or credit memo."
            ),
            status=TicketStatus.open,
            priority=TicketPriority.high,
            requester_id=9004,
            assignee_id=5003,
            tags=["billing", "invoice", "po-mismatch"],
            created_at=now - timedelta(days=8),
            updated_at=now - timedelta(days=2),
        ),
        ZendeskTicket(
            id=40063,
            subject="Data migration status update",
            description=(
                "Checking in on the status of our data migration from legacy "
                "on-prem to the hosted environment. Last update was two weeks ago "
                "and we're targeting a March 15 go-live. Please advise."
            ),
            status=TicketStatus.pending,
            priority=TicketPriority.normal,
            requester_id=9005,
            assignee_id=5001,
            tags=["migration", "onboarding", "follow-up"],
            created_at=now - timedelta(days=14),
            updated_at=now - timedelta(days=3),
        ),
        ZendeskTicket(
            id=40045,
            subject="Warehouse label printer not pulling item data",
            description=(
                "The Zebra ZD421 on Pick Station 3 prints blank labels. It was "
                "working fine until the P21 update last Friday. The other two "
                "stations are fine. We've restarted the print spooler twice."
            ),
            status=TicketStatus.solved,
            priority=TicketPriority.normal,
            requester_id=9006,
            assignee_id=5002,
            tags=["warehouse", "printing", "p21"],
            created_at=now - timedelta(days=18),
            updated_at=now - timedelta(days=10),
        ),
        ZendeskTicket(
            id=40029,
            subject="SSO login loop after Azure AD update",
            description=(
                "After our Azure AD tenant update, users hit a redirect loop "
                "when trying to SSO into the Luxor Workspaces portal. Clearing cookies "
                "doesn't fix it. Affects all Chrome users, Edge works fine."
            ),
            status=TicketStatus.closed,
            priority=TicketPriority.high,
            requester_id=9002,
            assignee_id=5003,
            tags=["sso", "azure-ad", "authentication"],
            created_at=now - timedelta(days=25),
            updated_at=now - timedelta(days=20),
        ),
    ]


_DEMO_USERS: dict[int, dict[str, Any]] = {
    9001: {"id": 9001, "name": "Maria Gonzalez", "email": "maria.gonzalez@acmedist.com", "role": "end-user"},
    9002: {"id": 9002, "name": "James Whitfield", "email": "j.whitfield@northstarlogistics.com", "role": "end-user"},
    9003: {"id": 9003, "name": "Priya Sharma", "email": "priya@tektonparts.com", "role": "end-user"},
    9004: {"id": 9004, "name": "Robert Chen", "email": "rchen@precisionmfg.com", "role": "end-user"},
    9005: {"id": 9005, "name": "Angela Torres", "email": "angela.torres@summitsupply.com", "role": "end-user"},
    9006: {"id": 9006, "name": "Kevin Draper", "email": "kdraper@greatlakesind.com", "role": "end-user"},
    5001: {"id": 5001, "name": "Luxor Support — Tier 1", "email": "support@luxorworkspaces.com", "role": "agent"},
    5002: {"id": 5002, "name": "Luxor Support — Tier 2", "email": "tier2@luxorworkspaces.com", "role": "agent"},
    5003: {"id": 5003, "name": "Luxor Support — Billing", "email": "billing@luxorworkspaces.com", "role": "agent"},
}


_DEMO_COMMENTS: dict[int, list[dict[str, Any]]] = {
    40112: [
        {
            "id": 80001,
            "body": (
                "We're trying to run the Inventory Valuation report in P21 "
                "and it hangs at 80% then times out."
            ),
            "author_id": 9001,
            "public": True,
            "created_at": (_demo_now() - timedelta(hours=6)).isoformat(),
        },
        {
            "id": 80002,
            "body": (
                "Hi Maria, we're looking into the report timeout now. "
                "Can you confirm which P21 version you're on? "
                "Also, was any SQL maintenance run over the weekend?"
            ),
            "author_id": 5001,
            "public": True,
            "created_at": (_demo_now() - timedelta(hours=4)).isoformat(),
        },
    ],
    40098: [
        {
            "id": 80010,
            "body": "EDI 856 sync broken since Tuesday. 401 on API gateway.",
            "author_id": 9002,
            "public": True,
            "created_at": (_demo_now() - timedelta(days=3)).isoformat(),
        },
    ],
}


# ── Real API Helpers ─────────────────────────────────────────────────────────

def _build_base_url() -> str:
    return f"https://{settings.zendesk_subdomain}.zendesk.com/api/v2"


def _build_auth_header() -> dict[str, str]:
    """Basic auth: base64("{email}/token:{api_token}")"""
    credentials = f"{settings.zendesk_email}/token:{settings.zendesk_api_token}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}


def _get_client() -> httpx.Client:
    return httpx.Client(
        base_url=_build_base_url(),
        headers={**_build_auth_header(), "Content-Type": "application/json"},
        timeout=30.0,
    )


def _parse_ticket(raw: dict[str, Any]) -> ZendeskTicket:
    return ZendeskTicket(
        id=raw["id"],
        subject=raw.get("subject") or "(no subject)",
        description=raw.get("description"),
        status=TicketStatus(raw.get("status", "open")),
        priority=TicketPriority(raw["priority"]) if raw.get("priority") else None,
        requester_id=raw.get("requester_id"),
        assignee_id=raw.get("assignee_id"),
        tags=raw.get("tags", []),
        created_at=raw.get("created_at"),
        updated_at=raw.get("updated_at"),
        raw=raw,
    )


# ── Ticket Read Operations ────────────────────────────────────────────────────

def list_tickets(
    status: str = "open",
    per_page: int = 25,
    page: int = 1,
) -> list[ZendeskTicket]:
    """List tickets filtered by status. Returns parsed ticket objects."""
    if DEMO_MODE:
        return [t for t in _demo_tickets() if t.status.value == status]

    with _get_client() as client:
        response = client.get(
            "/tickets",
            params={"status": status, "per_page": per_page, "page": page},
        )
        response.raise_for_status()
        return [_parse_ticket(t) for t in response.json().get("tickets", [])]


def get_ticket(ticket_id: int) -> ZendeskTicket:
    """Fetch a single ticket by ID."""
    if DEMO_MODE:
        for t in _demo_tickets():
            if t.id == ticket_id:
                return t
        raise ValueError(f"Demo ticket {ticket_id} not found")

    with _get_client() as client:
        response = client.get(f"/tickets/{ticket_id}")
        response.raise_for_status()
        return _parse_ticket(response.json()["ticket"])


def search_tickets(query: str, per_page: int = 25) -> list[ZendeskTicket]:
    """
    Search tickets using Zendesk search syntax.
    Example query: 'type:ticket status:open subject:"billing"'
    """
    if DEMO_MODE:
        q = query.lower()
        return [
            t for t in _demo_tickets()
            if q in t.subject.lower()
            or (t.description and q in t.description.lower())
            or any(q in tag for tag in t.tags)
        ]

    with _get_client() as client:
        response = client.get(
            "/search",
            params={"query": f"type:ticket {query}", "per_page": per_page},
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        return [_parse_ticket(t) for t in results if t.get("result_type") == "ticket"]


def get_tickets_by_requester(requester_id: int) -> list[ZendeskTicket]:
    """Fetch all tickets for a specific requester (user ID)."""
    if DEMO_MODE:
        return [t for t in _demo_tickets() if t.requester_id == requester_id]

    with _get_client() as client:
        response = client.get(f"/users/{requester_id}/tickets/requested")
        response.raise_for_status()
        return [_parse_ticket(t) for t in response.json().get("tickets", [])]


def get_ticket_comments(ticket_id: int) -> list[dict[str, Any]]:
    """Fetch all comments/conversation for a ticket."""
    if DEMO_MODE:
        return _DEMO_COMMENTS.get(ticket_id, [])

    with _get_client() as client:
        response = client.get(f"/tickets/{ticket_id}/comments")
        response.raise_for_status()
        return response.json().get("comments", [])


def get_user(user_id: int) -> dict[str, Any]:
    """Fetch a Zendesk user by ID."""
    if DEMO_MODE:
        if user_id in _DEMO_USERS:
            return _DEMO_USERS[user_id]
        return {"id": user_id, "name": "Unknown User", "email": "unknown@example.com"}

    with _get_client() as client:
        response = client.get(f"/users/{user_id}")
        response.raise_for_status()
        return response.json().get("user", {})


def find_user_by_email(email: str) -> dict[str, Any] | None:
    """Look up a Zendesk user by email address."""
    if DEMO_MODE:
        for user in _DEMO_USERS.values():
            if user["email"] == email:
                return user
        return None

    with _get_client() as client:
        response = client.get(
            "/users/search",
            params={"query": email},
        )
        response.raise_for_status()
        users = response.json().get("users", [])
        return users[0] if users else None


# ── Ticket Write Operations ───────────────────────────────────────────────────

def update_ticket(
    ticket_id: int,
    status: TicketStatus | None = None,
    priority: TicketPriority | None = None,
    tags_add: list[str] | None = None,
) -> ZendeskTicket:
    """Update ticket metadata (status, priority, tags)."""
    if DEMO_MODE:
        ticket = get_ticket(ticket_id)
        if status:
            ticket.status = status
        if priority:
            ticket.priority = priority
        if tags_add:
            ticket.tags.extend(tags_add)
        ticket.updated_at = _demo_now()
        logger.info("[DEMO] Updated ticket %d", ticket_id)
        return ticket

    payload: dict[str, Any] = {}
    if status:
        payload["status"] = status.value
    if priority:
        payload["priority"] = priority.value
    if tags_add:
        payload["additional_tags"] = tags_add

    with _get_client() as client:
        response = client.put(
            f"/tickets/{ticket_id}",
            json={"ticket": payload},
        )
        response.raise_for_status()
        return _parse_ticket(response.json()["ticket"])


def add_comment(comment: ZendeskComment) -> dict[str, Any]:
    """
    Add a public or internal comment to a ticket.
    Also updates ticket status to 'pending' (awaiting customer) for public comments
    or 'open' for internal notes.
    """
    if DEMO_MODE:
        logger.info(
            "[DEMO] Comment added to ticket %d (public=%s): %s",
            comment.ticket_id,
            comment.public,
            comment.body[:80],
        )
        return {
            "ticket": {"id": comment.ticket_id, "status": "pending" if comment.public else "open"},
            "comment": {"id": 99999, "body": comment.body, "public": comment.public},
        }

    new_status = "pending" if comment.public else "open"

    payload: dict[str, Any] = {
        "ticket": {
            "status": new_status,
            "comment": {
                "body": comment.body,
                "public": comment.public,
            },
        }
    }
    if comment.author_id:
        payload["ticket"]["comment"]["author_id"] = comment.author_id

    with _get_client() as client:
        response = client.put(
            f"/tickets/{comment.ticket_id}",
            json=payload,
        )
        response.raise_for_status()
        return response.json()


def create_ticket(
    subject: str,
    body: str,
    requester_email: str,
    requester_name: str | None = None,
    priority: TicketPriority = TicketPriority.normal,
    tags: list[str] | None = None,
) -> ZendeskTicket:
    """Create a new ticket — useful when processing inbound emails with no existing ticket."""
    if DEMO_MODE:
        new_ticket = ZendeskTicket(
            id=50001,
            subject=subject,
            description=body,
            status=TicketStatus.new,
            priority=priority,
            requester_id=9099,
            tags=tags or ["ai-created", "email-inbound"],
            created_at=_demo_now(),
            updated_at=_demo_now(),
        )
        logger.info("[DEMO] Created ticket %d: %s", new_ticket.id, subject)
        return new_ticket

    payload: dict[str, Any] = {
        "ticket": {
            "subject": subject,
            "comment": {"body": body},
            "requester": {"email": requester_email, "name": requester_name or requester_email},
            "priority": priority.value,
            "tags": tags or ["ai-created", "email-inbound"],
        }
    }

    with _get_client() as client:
        response = client.post("/tickets", json=payload)
        response.raise_for_status()
        return _parse_ticket(response.json()["ticket"])


# ── Health Check ──────────────────────────────────────────────────────────────

def check_connection() -> bool:
    """Verify Zendesk credentials and connectivity. Returns True on success."""
    if DEMO_MODE:
        logger.info("[DEMO] Zendesk health check — simulated OK")
        return True

    try:
        with _get_client() as client:
            response = client.get("/tickets/count")
            return response.status_code == 200
    except Exception as exc:
        logger.warning("Zendesk health check failed: %s", exc)
        return False
