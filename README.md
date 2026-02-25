# Luxor Workspaces CS Agent

AI-powered customer service agent for Luxor Workspaces.
Integrates Zendesk + Microsoft Outlook via Claude AI.

---

## What It Does

| Capability | How |
|---|---|
| Ticket classification | Claude analyzes subject + description → priority, category, sentiment, escalation flag |
| Response generation | Claude drafts on-brand replies using the Luxor Workspaces knowledge base |
| Email monitoring | Graph API polls support inbox for unread messages |
| Email-to-ticket matching | Finds existing Zendesk tickets by sender email |
| Customer history | AI summary of all tickets for a requester |
| Auto-send (optional) | Posts comments to Zendesk or sends replies via Graph |

---

## Quick Start (Local)

### 1. Prerequisites

- Python 3.11+
- pip

### 2. Install

```bash
cd C:\Claude\Work\Luxor\Projects\CS_GPT
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Configure

```bash
copy .env.example .env
# Edit .env — fill in Anthropic, Zendesk, and Azure credentials
```

### 4. Run

```bash
python server.py
# or
uvicorn server:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 5. Demo (no Zendesk/Azure credentials needed)

```
GET http://localhost:8000/demo
```

Returns a live Claude-generated ticket classification and response using mock Luxor Workspaces data.

---

## Environment Variables

See `.env.example` for all required variables.

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic Console → API Keys |
| `ZENDESK_SUBDOMAIN` | e.g. `luxorworkspaces` |
| `ZENDESK_EMAIL` | Agent email in Zendesk |
| `ZENDESK_API_TOKEN` | Zendesk Admin → Settings → API |
| `MS_TENANT_ID` | Azure AD tenant ID |
| `MS_CLIENT_ID` | App Registration client ID |
| `MS_CLIENT_SECRET` | App Registration client secret |
| `MS_MAILBOX` | Monitored mailbox UPN |
| `DEMO_MODE` | Set to `true` for demo mode (no external calls) |

---

## Azure App Registration (Microsoft Graph)

1. Azure Portal → Azure Active Directory → App registrations → New registration
2. Name: `LuxorCSAgent`, Supported account types: Single tenant
3. Certificates & secrets → New client secret → copy value to `MS_CLIENT_SECRET`
4. API permissions → Add permission → Microsoft Graph → Application permissions:
   - `Mail.Read`
   - `Mail.ReadWrite`
   - `Mail.Send`
   - `User.Read.All`
5. Grant admin consent
6. Copy Application (client) ID to `MS_CLIENT_ID`
7. Copy Directory (tenant) ID to `MS_TENANT_ID`

---

## Deploy to Azure Container Apps

See `deploy-instructions.md` for full step-by-step guide.

### Quick deploy:

```bash
chmod +x azure-deploy.sh
./azure-deploy.sh
```

---

## API Reference

| Method | Path | Description |
|---|---|---|
| GET | `/` | API info |
| GET | `/health` | Service connectivity check |
| GET | `/demo` | Live demo with mock data |
| GET | `/tickets` | List tickets (`?status=open`) |
| GET | `/tickets/search` | Search (`?q=billing`) |
| GET | `/tickets/{id}` | Get ticket |
| POST | `/tickets/{id}/classify` | AI classify |
| POST | `/tickets/{id}/respond` | AI respond (+ `auto_send`) |
| PUT | `/tickets/{id}/update` | Update status/comment |
| GET | `/emails/unread` | List unread emails |
| GET | `/emails/{id}` | Get email |
| POST | `/emails/{id}/process` | Classify + draft response |
| POST | `/emails/{id}/send` | Send response |
| GET | `/customers/{email}/history` | AI customer summary |

Full interactive docs at `/docs`.

---

## Architecture

```
                    ┌─────────────────────────────────────────────┐
                    │              Luxor Workspaces CS Agent API                │
                    │              (FastAPI / Azure)                │
                    └──────┬──────────────┬────────────────────────┘
                           │              │
              ┌────────────▼────┐    ┌────▼──────────────────┐
              │  zendesk_client │    │   outlook_client       │
              │  (httpx + Basic │    │   (MSAL + Graph API)   │
              │   Auth)         │    │                        │
              └────────────┬────┘    └────┬──────────────────┘
                           │              │
                    ┌──────▼──────────────▼──────┐
                    │         ai_engine           │
                    │    (Anthropic Claude API)   │
                    │                             │
                    │  - classify_ticket()        │
                    │  - generate_ticket_response │
                    │  - generate_email_response  │
                    │  - summarize_customer_history│
                    └─────────────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │       knowledge_base       │
                    │  (Luxor Workspaces policies, FAQ,      │
                    │   services, SLA, contacts) │
                    └───────────────────────────┘
```
