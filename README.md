# BookLeaf Author Support & Communication Portal

Authors raise support tickets. The BookLeaf team handles them faster with AI help
(auto-category, priority score, and a drafted reply). Every AI output can be overridden by a human.

## Tech stack and why
| Part | Choice | Why |
|---|---|---|
| Frontend | Next.js 14 (React) | Simple routing, separate author/admin areas |
| Backend | FastAPI (Python) | Fast, automatic validation, free Swagger docs at `/docs` |
| Database | PostgreSQL | Relational data (authors, books, tickets), good indexes |
| AI | Anthropic Claude Haiku 4.5 | See below |
| Real-time | Polling (6-10 sec) | Simple, reliable, works everywhere |

### Model choice: Claude Haiku
- Cheap and fast, which suits short tasks like classification and 100-word replies.
- Follows instructions and JSON format reliably.
- Supports prompt caching, so the fixed system prompt is billed at a lower rate on repeat calls.
- The model name is an env variable (`AI_MODEL`), so it can be swapped without code changes.

## How it works
1. Author submits a ticket. It is **saved first**, and the API replies at once.
2. A background task runs the AI pipeline: **one call** gives category + priority + confidence.
3. A second call writes a draft reply, which is **saved in the database** (never paid for twice).
4. Admin opens the ticket, sees the cached draft, edits it, and sends.
5. The author's page polls and shows the reply without a refresh.

## AI design
- **Prompts** (`backend/app/ai/prompts.py`): empathetic tone, own mistakes, real numbers, clear next step, 90-180 words.
- **Knowledge Base** is split by topic. Only the sections for the ticket's category are sent.
- **Real data:** the author's own book data is added to the prompt. Dates and money checks (next payout date, Rs. 1,000 minimum) are done in code, not by the AI.
- **Cost control:** 1 call for classify + priority, a trimmed ticket text (2,000 chars), only the last 2 messages, small `max_tokens`, prompt caching, drafts cached in DB, rate limit per author, and every call logged (tokens, time, result).
- **Failure handling:** 15s timeout, 1 retry. If the AI is down or returns bad JSON, tickets are still created, keyword rules assign category/priority, `ai_status = ai_failed`, and admins can write replies manually or click "Regenerate".
- **Safety:** ticket text is wrapped in `<ticket>` tags and treated as data (prompt-injection guard). The model only gets the current author's data. Replies never promise anything outside policy, and a human reviews every reply.
- **Accountability:** the original AI suggestion is stored next to the final value. `/api/admin/stats` shows how often admins accept the AI.

## Security
- API key only in backend `.env` (never in the frontend, never committed).
- Passwords hashed with bcrypt, JWT auth on every route except login and health.
- Role checks: authors see only their own books and tickets (other authors' tickets return 404). Admin routes return 403 for authors.
- Input validation with Pydantic. Errors use one JSON format, never a bare 500.

## Run locally
```bash
docker compose up -d                       # Postgres

cd backend
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                       # add ANTHROPIC_API_KEY (optional, app works without it)
python scripts/seed.py                     # 10 authors, 18 books, 1 admin
uvicorn app.main:app --reload              # http://localhost:8000/docs

cd ../frontend
cp .env.local.example .env.local
npm install
npm run dev                                # http://localhost:3000
```
Tests: `cd backend && pytest`

**Logins:** author `priya.sharma@email.com` / `Author@123` (all authors share this password), admin `admin@bookleaf.com` / `Admin@123`.

## API reference
Base URL `http://localhost:8000`. Send `Authorization: Bearer <token>` on all routes except login and health.
Interactive docs: `/docs`.

| Method | Endpoint | Role | Description |
|---|---|---|---|
| POST | `/api/auth/login` | Public | Log in, returns JWT |
| GET | `/api/auth/me` | Any | Current user |
| GET | `/api/books` | Author | My books |
| POST | `/api/tickets` | Author | Create ticket. Optional `Idempotency-Key` header stops duplicates |
| GET | `/api/tickets` | Author | My tickets with replies |
| GET | `/api/tickets/{id}` | Author | One of my tickets |
| GET | `/api/admin/tickets` | Admin | Queue. Filters: `status, category, priority, date_from, date_to, mine, page, page_size` |
| GET | `/api/admin/tickets/{id}` | Admin | Detail with AI draft, notes, author and book |
| PATCH | `/api/admin/tickets/{id}` | Admin | Change status, category, priority |
| POST | `/api/admin/tickets/{id}/assign-me` | Admin | Assign to myself |
| POST | `/api/admin/tickets/{id}/reply` | Admin | Send reply (author sees it) |
| POST | `/api/admin/tickets/{id}/notes` | Admin | Add internal note |
| POST | `/api/admin/tickets/{id}/draft/regenerate` | Admin | New AI draft |
| GET | `/api/admin/stats` | Admin | AI accuracy, tokens, cost |
| GET | `/health` | Public | Health check |

**Error format** (all errors):
```json
{ "error": { "code": "validation_error", "message": "Some fields are invalid.", "details": [{"field": "subject", "message": "..."}] } }
```
Status codes: 401 not logged in, 403 wrong role, 404 not found, 422 invalid input, 429 rate limited, 503 AI unavailable.

## Known limits (honest notes)
- Attachment is UI only (file name saved, no upload).
- Tables are created with `create_all`. Alembic migrations would be used in production.
- Rate limiter and caches are in memory. Production would use Redis.
- JWT is kept in localStorage for simplicity. Production would use httpOnly cookies.
- Bank-details status is not in the dataset, so the AI is told it is "unknown" and asks the author to confirm.
- Polling every few seconds. SSE would be the next step for scale.