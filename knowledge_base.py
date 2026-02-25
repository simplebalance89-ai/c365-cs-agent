"""
knowledge_base.py — Luxor Workspaces knowledge for AI response generation.

This module provides structured knowledge the AI engine injects into prompts
so Claude generates accurate, on-brand responses without hallucinating
Luxor Workspaces-specific details.
"""

from __future__ import annotations

# ── Company Overview ──────────────────────────────────────────────────────────

COMPANY_OVERVIEW = """
Luxor Workspaces is a premium coworking and shared workspace company offering
flexible office solutions for professionals, startups, and growing businesses.
We provide private offices, hot desks, dedicated desks, conference rooms,
event spaces, and a full suite of business amenities. Our spaces are designed
for productivity, collaboration, and growth — with 24/7 access, high-speed
WiFi, mail handling, printing, and on-site support. Members range from solo
freelancers to teams of 50+ across technology, creative, legal, financial,
and professional services.
"""

# ── Services Catalog ─────────────────────────────────────────────────────────

SERVICES = {
    "hot_desk": {
        "name": "Hot Desk Membership",
        "description": "Flexible seating in our open workspace. First-come, first-served desk access "
                       "during business hours or 24/7 depending on plan. Includes WiFi, printing, "
                       "coffee/tea, and access to common areas.",
        "pricing": "$299/month per desk",
        "includes": ["High-speed WiFi", "Printing (50 pages/month)", "Coffee and tea bar",
                     "Mail handling", "2 hours conference room/month", "Community events access"],
    },
    "dedicated_desk": {
        "name": "Dedicated Desk",
        "description": "Your own permanent desk in a shared space. Keep your setup, leave your things. "
                       "24/7 access, lockable storage, and all hot desk perks included.",
        "pricing": "$499/month per desk",
        "includes": ["24/7 access", "Lockable storage", "Ergonomic chair", "All hot desk perks",
                     "4 hours conference room/month", "Mail handling with suite number"],
    },
    "private_office": {
        "name": "Private Office",
        "description": "Fully enclosed private offices for teams of 1-20+. Furnished, lockable, "
                       "with dedicated climate control. Includes all membership perks plus dedicated "
                       "phone line and enhanced conference room hours.",
        "pricing": "$850 - $5,000+/month (based on size and floor)",
        "sizes": ["1-person (solo studio)", "2-4 person", "5-10 person", "10-20+ person (enterprise)"],
        "includes": ["24/7 access", "Furniture included", "Dedicated climate control",
                     "10 hours conference room/month", "Mail handling with suite number",
                     "Phone line", "Signage on door"],
    },
    "conference_rooms": {
        "name": "Conference Room Booking",
        "description": "Professional meeting rooms with video conferencing, whiteboards, and catering options. "
                       "Bookable by the hour or as part of a membership plan. Recurring bookings available.",
        "pricing": "$25-75/hour (member rates), $50-125/hour (non-member)",
        "rooms": ["Huddle rooms (2-4 people)", "Boardroom 1 (8 people)", "Boardroom 2 (12 people)",
                  "Training room (20 people)", "Event space (50+ people)"],
    },
    "virtual_office": {
        "name": "Virtual Office",
        "description": "Professional business address, mail handling, and receptionist services "
                       "without a physical desk. Perfect for remote workers who need a professional presence.",
        "pricing": "$99/month",
        "includes": ["Business address for registration", "Mail receiving and forwarding",
                     "Phone answering service", "2 hours conference room/month",
                     "Access to common areas during business hours"],
    },
    "event_space": {
        "name": "Event Space Rental",
        "description": "Host workshops, networking events, product launches, and team offsites "
                       "in our flexible event spaces. Catering and AV equipment available.",
        "pricing": "$500-2,000 per event (varies by space and duration)",
        "includes": ["AV equipment", "Flexible seating arrangements", "Catering coordination",
                     "Event support staff", "WiFi for all attendees"],
    },
}

# ── Policies ─────────────────────────────────────────────────────────────────

POLICIES = {
    "membership_terms": {
        "agreement": "All memberships are governed by a signed Membership Agreement that defines "
                     "the plan type, term, pricing, and included amenities. No access is granted "
                     "without a signed agreement.",
        "term": "Month-to-month memberships require 30 days notice to cancel. Annual memberships "
                "receive a 10% discount and require 60 days notice.",
        "modifications": "Plan upgrades take effect immediately. Downgrades take effect at the next "
                         "billing cycle. Pro-rated credits are applied for mid-cycle upgrades.",
    },
    "billing": {
        "payment_terms": "Memberships are billed monthly in advance on the 1st of each month. "
                         "Conference room overages and add-on services are billed at month end.",
        "accepted_methods": ["ACH / wire transfer (preferred)", "Credit card",
                             "Check (payable to Luxor Workspaces LLC)"],
        "late_payment": "A late fee of 1.5% per month applies to balances past due beyond 15 days. "
                        "Luxor Workspaces reserves the right to suspend access on accounts more than 30 days past due.",
        "deposits": "Private office leases require first and last month deposit. "
                    "All other memberships are billed monthly in advance with no deposit.",
    },
    "facilities": {
        "access_hours": "Hot desk members: business hours (7 AM - 9 PM). Dedicated desk and private "
                        "office members: 24/7 access with key card. Event spaces by reservation only.",
        "guest_policy": "Members may bring up to 2 guests per day at no charge. Additional guests "
                        "are $15/day each. All guests must check in at reception.",
        "noise_policy": "Phone calls and video meetings should be taken in phone booths or conference "
                        "rooms. The open workspace is a professional, low-noise environment.",
        "maintenance": "Facilities issues should be reported via the support portal or front desk. "
                       "Emergency maintenance (HVAC, plumbing, electrical) is handled within 1 hour. "
                       "Non-emergency requests within 24 hours.",
    },
    "data_handling": {
        "security": "All member data is encrypted in transit (TLS 1.2+) and at rest (AES-256). "
                    "Building access is secured with key card entry and 24/7 security cameras.",
        "wifi_security": "Enterprise-grade WiFi with WPA3 encryption. Each member gets unique "
                         "login credentials. Network is segmented for privacy.",
        "mail_handling": "Packages and mail are received at the front desk, logged, and members are "
                         "notified via email. Items are held for up to 14 days before return to sender.",
    },
}

# ── SLA Standards ─────────────────────────────────────────────────────────────

SLA = {
    "response_times": {
        "critical": "1 hour (facility emergency, safety issue, security breach)",
        "high": "4 hours (HVAC failure, WiFi outage, access issue)",
        "normal": "1 business day (booking questions, billing inquiries, general requests)",
        "low": "3 business days (suggestions, feedback, non-urgent requests)",
    },
    "escalation_triggers": [
        "Facility emergency (fire, flood, electrical, safety hazard)",
        "Building access system failure",
        "Security incident or suspected breach",
        "Member executive escalation",
        "SLA response time missed",
        "Second repeat issue on same root cause",
        "Billing dispute over $500",
        "WiFi or IT infrastructure outage affecting multiple members",
        "Legal language or termination threat in communication",
    ],
    "escalation_contact": "management@luxorworkspaces.com (Luxor Workspaces Management)",
}

# ── FAQ ───────────────────────────────────────────────────────────────────────

FAQ = [
    {
        "q": "What types of workspace plans do you offer?",
        "a": "We offer hot desks ($299/month), dedicated desks ($499/month), private offices "
             "($850-$5,000+/month based on size), virtual offices ($99/month), and conference room "
             "rentals. All plans include WiFi, printing, and access to common areas.",
    },
    {
        "q": "Can I tour the space before signing up?",
        "a": "Absolutely! We offer free tours Monday through Friday during business hours. You can "
             "book a tour through our website at luxorworkspaces.com or just walk in and ask at the "
             "front desk. We also offer a free day pass so you can try the space before committing.",
    },
    {
        "q": "How do I book a conference room?",
        "a": "Log into your member portal at members.luxorworkspaces.com, navigate to Conference Rooms, "
             "and select your preferred room, date, and time. You can also set up recurring bookings. "
             "Conference room hours are included in your plan, with overage billed at member rates.",
    },
    {
        "q": "What are the access hours?",
        "a": "Hot desk members have access during business hours (7 AM - 9 PM, Monday-Friday). "
             "Dedicated desk and private office members have 24/7 key card access. The front desk "
             "is staffed Monday-Friday 8 AM - 6 PM.",
    },
    {
        "q": "Is the WiFi secure and reliable?",
        "a": "Yes. We provide enterprise-grade WiFi with WPA3 encryption. Each member gets unique "
             "login credentials on a segmented network for privacy. Our infrastructure includes "
             "redundant connections and is monitored 24/7.",
    },
    {
        "q": "How does mail and package handling work?",
        "a": "All mail and packages are received at the front desk, logged in our system, and you "
             "receive an email notification. Dedicated desk and private office members get a suite "
             "number for their business address. Items are held for up to 14 days.",
    },
    {
        "q": "Can I bring guests to the workspace?",
        "a": "Yes! Members may bring up to 2 guests per day at no charge. Additional guests are "
             "$15/day each. All guests must check in at reception and follow our community guidelines.",
    },
    {
        "q": "What is included in a private office?",
        "a": "Private offices come fully furnished with desks, chairs, and storage. They include "
             "24/7 access, dedicated climate control, 10 hours of conference room time per month, "
             "mail handling with a suite number, a phone line, and door signage.",
    },
    {
        "q": "How do I report a facilities issue?",
        "a": "You can report issues through the member portal, by emailing support@luxorworkspaces.com, "
             "or by visiting the front desk. Emergency facilities issues (HVAC, plumbing, electrical) "
             "are handled within 1 hour. Non-emergency requests within 24 hours.",
    },
    {
        "q": "What is your cancellation policy?",
        "a": "Month-to-month memberships require 30 days written notice to cancel. Annual memberships "
             "require 60 days notice. There are no early termination fees for month-to-month plans. "
             "Pro-rated refunds are provided for any prepaid unused period.",
    },
    {
        "q": "Do you offer discounts for multiple desks or long-term commitments?",
        "a": "Yes. We offer a Growth Tier discount when adding multiple desks and a 10% discount on "
             "annual commitments. We also have a Loyalty Upgrade Incentive for existing members who "
             "upgrade their plan. Contact us for a custom quote for teams of 5+.",
    },
    {
        "q": "How do I get started?",
        "a": "Visit our website at luxorworkspaces.com to book a tour, or email info@luxorworkspaces.com. "
             "You can also walk into any of our locations during business hours. We will help you find "
             "the right plan and can have you set up the same day.",
    },
]

# ── Contact Directory ─────────────────────────────────────────────────────────

CONTACTS = {
    "support": "support@luxorworkspaces.com",
    "sales": "info@luxorworkspaces.com",
    "billing": "billing@luxorworkspaces.com",
    "management": "management@luxorworkspaces.com",
    "escalation": "management@luxorworkspaces.com",
}

# ── Brand Voice Guidelines ────────────────────────────────────────────────────

BRAND_VOICE = """
Luxor Workspaces brand voice:
- Professional, warm, and community-oriented. We create spaces where great work happens.
- Solutions-focused. Every response moves the conversation toward a clear next step.
- Direct and helpful. We make workspace simple and stress-free.
- Concise. Our members are busy professionals. Respect their time.
- Empathetic to workspace frustrations. We understand what a broken printer or noisy neighbor costs in productivity.
- First-person plural ("we", "our team") represents the Luxor Workspaces team.
- Sign off: "The Luxor Workspaces Team" for general CS, or agent first name for account-level interactions.
- Never promise timelines or outcomes we cannot deliver. Use "Let me check with our facilities team and follow up" over guessing.
- Welcoming to new members and appreciative of loyal ones.
- Confident but not corporate. We are hospitality professionals, not bureaucrats.
"""

# ── Utility: Build context string for AI prompts ──────────────────────────────

def build_knowledge_context(categories: list[str] | None = None) -> str:
    """
    Returns a formatted knowledge context string for injection into AI prompts.
    Pass specific category keys (e.g. ["billing", "sow_terms"]) to scope the context,
    or None to include all.
    """
    sections: list[str] = [
        f"COMPANY OVERVIEW:\n{COMPANY_OVERVIEW.strip()}",
        f"BRAND VOICE:\n{BRAND_VOICE.strip()}",
        f"SLA STANDARDS:\n{_format_dict(SLA)}",
        f"ESCALATION CONTACT: {SLA['escalation_contact']}",
    ]

    policy_keys = categories if categories else list(POLICIES.keys())
    relevant_policies = {k: POLICIES[k] for k in policy_keys if k in POLICIES}
    if relevant_policies:
        sections.append(f"RELEVANT POLICIES:\n{_format_dict(relevant_policies)}")

    # Include FAQ always — it's short and very useful
    faq_text = "\n".join(f"Q: {item['q']}\nA: {item['a']}" for item in FAQ)
    sections.append(f"FAQ:\n{faq_text}")

    sections.append(f"CONTACT DIRECTORY:\n{_format_dict(CONTACTS)}")

    return "\n\n".join(sections)


def _format_dict(d: dict, indent: int = 0) -> str:
    lines = []
    prefix = "  " * indent
    for key, value in d.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(_format_dict(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{prefix}{key}: {', '.join(str(v) for v in value)}")
        else:
            lines.append(f"{prefix}{key}: {value}")
    return "\n".join(lines)
