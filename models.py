"""
models.py — Pydantic models for tickets, emails, AI responses, and API payloads.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


# ── Enums ─────────────────────────────────────────────────────────────────────

class TicketPriority(str, Enum):
    urgent = "urgent"
    high = "high"
    normal = "normal"
    low = "low"


class TicketStatus(str, Enum):
    new = "new"
    open = "open"
    pending = "pending"
    hold = "hold"
    solved = "solved"
    closed = "closed"


class TicketCategory(str, Enum):
    billing = "billing"
    access = "access"
    maintenance = "maintenance"
    booking = "booking"
    lease = "lease"
    amenities = "amenities"
    orders = "orders"
    warranty = "warranty"
    general = "general"
    escalation = "escalation"


class SentimentLabel(str, Enum):
    positive = "positive"
    neutral = "neutral"
    frustrated = "frustrated"
    angry = "angry"


# ── Zendesk Models ────────────────────────────────────────────────────────────

class ZendeskRequester(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None


class ZendeskTicket(BaseModel):
    id: int
    subject: str
    description: Optional[str] = None
    status: TicketStatus
    priority: Optional[TicketPriority] = None
    requester_id: Optional[int] = None
    assignee_id: Optional[int] = None
    tags: list[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    raw: dict[str, Any] = Field(default_factory=dict, exclude=True)


class ZendeskComment(BaseModel):
    ticket_id: int
    body: str
    public: bool = True
    author_id: Optional[int] = None


class ZendeskTicketUpdateRequest(BaseModel):
    ticket_id: int
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    comment: Optional[str] = None
    public_comment: bool = True
    tags: Optional[list[str]] = None


# ── Email Models ──────────────────────────────────────────────────────────────

class InboundEmail(BaseModel):
    message_id: str
    subject: str
    sender_name: Optional[str] = None
    sender_email: str
    body_text: str
    body_html: Optional[str] = None
    received_at: Optional[datetime] = None
    thread_id: Optional[str] = None


class OutboundEmail(BaseModel):
    to: list[str]
    subject: str
    body_html: str
    reply_to_message_id: Optional[str] = None


# ── AI Engine Models ──────────────────────────────────────────────────────────

class TicketClassification(BaseModel):
    ticket_id: Optional[int] = None
    category: TicketCategory
    priority: TicketPriority
    sentiment: SentimentLabel
    should_escalate: bool
    escalation_reason: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str


class SuggestedResponse(BaseModel):
    ticket_id: Optional[int] = None
    subject: str
    body: str
    suggested_status: TicketStatus
    suggested_tags: list[str] = Field(default_factory=list)
    internal_notes: Optional[str] = None


class CustomerHistorySummary(BaseModel):
    requester_email: str
    total_tickets: int
    open_tickets: int
    avg_sentiment: str
    top_categories: list[str]
    summary: str
    vip_flag: bool = False


# ── API Request/Response Envelopes ────────────────────────────────────────────

class ClassifyRequest(BaseModel):
    ticket_id: int


class RespondRequest(BaseModel):
    ticket_id: int
    auto_send: bool = False          # if True, post comment to Zendesk automatically


class ProcessEmailRequest(BaseModel):
    message_id: str
    auto_reply: bool = False


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    services: dict[str, str]


class DemoResponse(BaseModel):
    demo_ticket: ZendeskTicket
    classification: TicketClassification
    suggested_response: SuggestedResponse
    demo_email: InboundEmail
    email_draft: SuggestedResponse
    message: str
