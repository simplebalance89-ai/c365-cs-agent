"""
knowledge_base.py — Conveyance365 (C365) knowledge for AI response generation.

This module provides structured knowledge the AI engine injects into prompts
so Claude generates accurate, on-brand responses without hallucinating
C365-specific details.
"""

from __future__ import annotations

# ── Company Overview ──────────────────────────────────────────────────────────

COMPANY_OVERVIEW = """
Conveyance365 (C365) is a technology consulting firm specializing in ERP
optimization and AI automation for mid-market manufacturers and distributors.
We help companies get more out of their existing ERP investments — Epicor P21,
NetSuite, and similar platforms — by combining deep system expertise with
purpose-built AI agents that automate manual workflows, improve data quality,
and deliver real-time operational intelligence. Our clients typically range
from $10M to $500M in annual revenue across manufacturing, distribution,
and industrial services.
"""

# ── Services Catalog ─────────────────────────────────────────────────────────

SERVICES = {
    "erp_health_check": {
        "name": "ERP Health Check",
        "description": "Comprehensive audit of your current ERP environment. We assess data quality, "
                       "workflow efficiency, integration gaps, unused modules, and optimization opportunities. "
                       "Delivered as a prioritized action plan with ROI estimates.",
        "pricing": "$5,000 flat fee",
        "duration": "2-3 weeks",
        "deliverables": ["Current-state assessment report", "Data quality scorecard",
                         "Prioritized optimization roadmap", "ROI projection for top 5 recommendations"],
        "platforms": ["Epicor P21", "NetSuite", "Sage", "Infor"],
    },
    "ai_agent_suite": {
        "name": "AI Agent Suite",
        "description": "Custom-built AI agents that automate repetitive ERP tasks. Agents handle "
                       "customer service inquiries, purchase order processing, inventory alerts, "
                       "quote generation, vendor communication, and more. Each agent is configured "
                       "per client and tailored to your specific business rules and ERP schema.",
        "pricing": "$2,500 - $15,000/month subscription (based on agent count and complexity)",
        "setup_fee": "One-time implementation fee based on scope (typically $5,000 - $25,000)",
        "includes": ["Agent configuration and deployment", "ERP integration",
                     "Ongoing model tuning", "Monthly performance reporting",
                     "Dedicated support channel"],
        "common_agents": ["Customer Service Agent", "PO Processing Agent", "Inventory Alert Agent",
                          "Quote Generation Agent", "Vendor Communication Agent",
                          "Collections Follow-Up Agent"],
    },
    "data_migration": {
        "name": "Data Migration & Cleanup",
        "description": "Full-service data migration between ERP systems or major data cleanup within "
                       "your existing platform. Includes data mapping, validation rules, duplicate "
                       "resolution, and post-migration verification.",
        "pricing": "$150/hr",
        "typical_engagements": ["Legacy system to P21 migration", "P21 version upgrades",
                                "Customer/vendor master cleanup", "Item master standardization",
                                "Historical data archival"],
    },
    "custom_reports": {
        "name": "Custom Report Development",
        "description": "Custom reports, dashboards, and analytics built on your ERP data. "
                       "Crystal Reports, SSRS, Power BI, or direct SQL. We build what your "
                       "team actually needs to make decisions.",
        "pricing": "$175/hr",
        "platforms": ["Crystal Reports", "SSRS", "Power BI", "Excel/SQL direct"],
        "examples": ["Sales performance dashboards", "Inventory aging analysis",
                     "Margin reporting by customer/product", "AR aging with collection priority scoring",
                     "Warehouse throughput metrics"],
    },
    "integration_services": {
        "name": "P21/NetSuite Integration Services",
        "description": "Build and maintain integrations between your ERP and external systems. "
                       "EDI, eCommerce, CRM, shipping, payment processing, and custom API work. "
                       "We handle the middleware, mapping, error handling, and monitoring.",
        "pricing": "$200/hr",
        "common_integrations": ["EDI (SPS Commerce, TrueCommerce)", "Shopify / BigCommerce / Magento",
                                "Salesforce / HubSpot CRM", "ShipStation / UPS / FedEx",
                                "Payment gateways", "Custom REST/SOAP APIs"],
        "platforms": ["Epicor P21", "NetSuite", "Celigo", "Boomi", "Custom middleware"],
    },
    "support_retainer": {
        "name": "Ongoing Support Retainer",
        "description": "Dedicated monthly hours for ongoing ERP support, troubleshooting, "
                       "minor enhancements, user training, and system administration. "
                       "Your team gets a direct line to C365 engineers without project-level overhead.",
        "tiers": {
            "standard": "10 hours/month at $175/hr ($1,750/mo)",
            "professional": "20 hours/month at $165/hr ($3,300/mo)",
            "enterprise": "40 hours/month at $150/hr ($6,000/mo)",
        },
        "includes": ["Dedicated account manager", "Priority queue access",
                     "Monthly usage reporting", "Rollover of unused hours (up to 25%)",
                     "Quarterly business review"],
    },
}

# ── Policies ─────────────────────────────────────────────────────────────────

POLICIES = {
    "sow_terms": {
        "scope": "All project work is governed by a signed Statement of Work (SOW) that defines "
                 "scope, deliverables, timeline, acceptance criteria, and pricing. No work begins "
                 "without a signed SOW.",
        "change_orders": "Any work outside the original SOW scope requires a written Change Order "
                         "signed by both parties before work begins. Change Orders specify additional "
                         "scope, timeline impact, and cost. Verbal approvals are not binding.",
        "acceptance": "Deliverables are subject to a 10 business day acceptance period after delivery. "
                      "If no feedback is received within the acceptance period, deliverables are "
                      "considered accepted.",
    },
    "billing": {
        "payment_terms": "Net-30 from invoice date. Invoices issued on the 1st and 15th of each month "
                         "for time-and-materials work. Fixed-fee projects invoiced per milestone schedule "
                         "defined in the SOW.",
        "accepted_methods": ["ACH / wire transfer (preferred)", "Credit card (3% processing fee)",
                             "Check (payable to Conveyance365 LLC)"],
        "late_payment": "A late fee of 1.5% per month applies to balances past due beyond 15 days. "
                        "C365 reserves the right to suspend services on accounts more than 45 days past due.",
        "deposits": "Fixed-fee projects require a 50% deposit before work begins. "
                    "Retainer clients are invoiced monthly in advance.",
    },
    "sla_response": {
        "retainer_clients": "Retainer clients receive priority queue access with guaranteed response "
                            "times per the SLA table. Response time is measured from ticket submission "
                            "to first meaningful response (not auto-acknowledgment).",
        "project_clients": "Active project clients receive standard response times. Support outside "
                           "project scope is billed at the applicable hourly rate.",
        "after_hours": "Critical (system down) issues are supported 24/7 for Enterprise retainer clients. "
                       "All other tiers: business hours only (Monday-Friday 8 AM - 6 PM ET).",
    },
    "ip_ownership": {
        "client_ip": "All custom code, reports, configurations, and deliverables created specifically "
                     "for the client under an SOW become the client's intellectual property upon "
                     "final payment.",
        "c365_ip": "C365 retains ownership of all pre-existing tools, frameworks, libraries, and "
                   "methodologies used in delivery. Client receives a perpetual, non-exclusive license "
                   "to use any C365 IP embedded in their deliverables.",
        "ai_agents": "AI Agent Suite subscriptions are licensed, not sold. Agent configurations, "
                     "training data, and prompt engineering remain C365 IP. Client data processed "
                     "by agents remains client property at all times.",
    },
    "data_handling": {
        "security": "All client data is encrypted in transit (TLS 1.2+) and at rest (AES-256). "
                    "C365 engineers access client systems only through approved, audited channels.",
        "environments": "Development and testing use anonymized or synthetic data wherever possible. "
                        "Production data access requires explicit client authorization.",
        "retention": "Client data is retained only for the duration of the active engagement plus "
                     "90 days. Upon request or engagement end, all client data is securely purged "
                     "and a certificate of destruction is provided.",
        "compliance": "C365 supports SOC 2 Type II compliance requirements. We sign BAAs for "
                      "clients in regulated industries upon request.",
    },
    "nda": {
        "standard": "C365 executes mutual NDAs with all clients before any discovery or scoping work. "
                    "Our standard NDA covers a 3-year confidentiality period.",
        "custom": "We accept client-provided NDAs. Legal review turnaround is 3-5 business days.",
    },
}

# ── SLA Standards ─────────────────────────────────────────────────────────────

SLA = {
    "response_times": {
        "critical": "1 hour (production system down, data loss, security breach)",
        "high": "4 hours (major feature broken, significant workflow disruption)",
        "normal": "1 business day (minor issues, questions, enhancement requests)",
        "low": "3 business days (cosmetic issues, documentation, nice-to-haves)",
    },
    "escalation_triggers": [
        "Production ERP system down or inaccessible",
        "Data integrity issue affecting orders, inventory, or financials",
        "Security incident or suspected breach",
        "Client executive escalation",
        "SLA response time missed",
        "Second repeat issue on same root cause",
        "Billing dispute over $2,000",
        "Integration failure causing order processing stoppage",
        "Legal language or termination threat in communication",
    ],
    "escalation_contact": "andrew@conveyance365.com (Andrew Gianelli, CEO)",
}

# ── FAQ ───────────────────────────────────────────────────────────────────────

FAQ = [
    {
        "q": "What ERP systems do you support?",
        "a": "Our primary expertise is Epicor Prophet 21 (P21) and NetSuite. We also work with "
             "Sage, Infor, and other mid-market ERP platforms. If you are on a system we have not "
             "listed, reach out and we will let you know if we can help.",
    },
    {
        "q": "How does the ERP Health Check work?",
        "a": "We connect to your environment, review your configuration, data quality, workflows, "
             "and integrations over 2-3 weeks. You receive a detailed report with a prioritized "
             "roadmap and ROI estimates. The $5,000 flat fee covers everything. No surprises.",
    },
    {
        "q": "What are AI agents and how do they work with my ERP?",
        "a": "AI agents are purpose-built automations that sit on top of your ERP and handle "
             "repetitive tasks. For example, a Customer Service Agent can answer order status "
             "questions, a PO Processing Agent can read and enter purchase orders, and an Inventory "
             "Alert Agent can flag stock issues before they become problems. They connect to your "
             "ERP through secure APIs and follow your business rules.",
    },
    {
        "q": "How long does it take to deploy an AI agent?",
        "a": "A standard single-agent deployment takes 3-6 weeks from signed SOW to production. "
             "This includes discovery, configuration, integration, testing, and go-live. More complex "
             "multi-agent deployments may take 8-12 weeks.",
    },
    {
        "q": "Is my data safe with C365?",
        "a": "Yes. All data is encrypted in transit and at rest. We access client systems only through "
             "approved, audited channels. We sign NDAs before any engagement and support SOC 2 and "
             "BAA requirements for regulated industries. Your data is never used to train models or "
             "shared with third parties.",
    },
    {
        "q": "What does the onboarding process look like?",
        "a": "After signing the SOW, we schedule a kickoff call with your team to align on goals, "
             "timelines, and access requirements. We then set up secure connectivity to your environment, "
             "conduct discovery, and begin execution. You will have a dedicated account manager and "
             "regular status updates throughout.",
    },
    {
        "q": "Can you integrate our ERP with our eCommerce platform?",
        "a": "Absolutely. We have built integrations with Shopify, BigCommerce, Magento, and custom "
             "eCommerce platforms. We handle product sync, order flow, inventory updates, pricing, "
             "and customer data mapping. Typical eCommerce-to-ERP integrations take 4-8 weeks.",
    },
    {
        "q": "How does pricing work for the AI Agent Suite?",
        "a": "The AI Agent Suite is a monthly subscription ranging from $2,500 to $15,000 per month "
             "depending on the number of agents and complexity. There is a one-time setup fee "
             "(typically $5,000 to $25,000) for initial configuration and integration. We scope "
             "everything upfront so you know the cost before committing.",
    },
    {
        "q": "Do you offer ongoing support after a project is complete?",
        "a": "Yes. We offer Support Retainer plans at 10, 20, or 40 hours per month. Retainer clients "
             "get priority response times, a dedicated account manager, and quarterly business reviews. "
             "Unused hours roll over up to 25%.",
    },
    {
        "q": "What if the project scope changes mid-engagement?",
        "a": "Scope changes are handled through a formal Change Order process. We document the additional "
             "scope, timeline impact, and cost, and both parties sign before any new work begins. "
             "This protects you from scope creep and ensures transparency.",
    },
    {
        "q": "Do you work with companies outside manufacturing and distribution?",
        "a": "Our sweet spot is mid-market manufacturers and distributors, but we have also served "
             "clients in industrial services, building materials, food and beverage distribution, "
             "and specialty chemicals. If your business runs on an ERP, we can likely help.",
    },
    {
        "q": "How do I get started?",
        "a": "Email sales@conveyance365.com or reach out to your contact at C365. We will schedule "
             "a 30-minute discovery call to understand your needs, then provide a scoping proposal "
             "within one week. No commitment required to have the conversation.",
    },
    {
        "q": "Who owns the deliverables at the end of a project?",
        "a": "All custom code, reports, and configurations built specifically for you become your "
             "intellectual property upon final payment. AI Agent subscriptions are licensed services. "
             "Your data is always yours, no matter what.",
    },
    {
        "q": "What is your cancellation policy for retainers?",
        "a": "Retainer agreements require 30 days written notice to cancel. There are no early "
             "termination fees. Any prepaid unused hours for the final month are refunded.",
    },
]

# ── Contact Directory ─────────────────────────────────────────────────────────

CONTACTS = {
    "support": "support@conveyance365.com",
    "sales": "sales@conveyance365.com",
    "billing": "billing@conveyance365.com",
    "ceo": "andrew@conveyance365.com (Andrew Gianelli)",
    "cto": "peter.wilson@conveyance365.com (Peter Wilson)",
    "escalation": "andrew@conveyance365.com",
}

# ── Brand Voice Guidelines ────────────────────────────────────────────────────

BRAND_VOICE = """
Conveyance365 brand voice:
- Professional and knowledgeable. We speak ERP fluently.
- Solutions-focused. Every response moves the conversation toward a clear next step.
- Direct and honest. We do not oversell. We show results and let the work speak.
- Concise. Our clients are busy operators. Respect their time.
- Empathetic to operational pain. We understand what a broken integration or bad data costs.
- First-person plural ("we", "our team") represents the C365 team.
- Sign off: "The Conveyance365 Team" for general CS, or agent first name for account-level interactions.
- Never promise timelines or outcomes we cannot deliver. Use "Let me review this with our team and follow up" over guessing.
- No jargon for the sake of jargon. Explain technical concepts in business terms when speaking with non-technical stakeholders.
- Confident but not arrogant. We are experts, not lecturers.
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
