# BookLeaf Author Support Portal

A web app where BookLeaf authors raise support tickets and the support team answers them faster, with AI doing the first draft. A human always checks the answer before it goes to the author.

## What it does

**For authors**
- Log in and see only their own books (ISBN, sales, royalty earned, paid and pending).
- Raise a support ticket for a book or for their account in general.
- See the status of their tickets and the team's replies. New replies show up on their own, no page refresh needed.

**For the support team (admin)**
- See all tickets in one queue. Filter by status, category, priority and date. Urgent and old tickets stand out.
- AI sets the category and the priority. The admin can change both.
- AI writes a draft reply using BookLeaf's policies and the author's real data. The admin edits it and sends it.
- Change ticket status, add private notes (the author never sees these) and assign a ticket to themselves.
- A stats page shows how often the team keeps the AI's suggestions, and how many AI calls were made.

## How a ticket moves
1. The author submits a ticket. It is **saved first**, so it is never lost.
2. In the background, the AI picks a category and priority, then writes a draft reply.
3. The admin opens the ticket and the draft is already there. They edit it and send it.
4. The author sees the reply within a few seconds.

## Tech used
| Frontend | Next.js (React) |
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| AI | Google Gemini |
| Live updates | Polling (the page asks for updates every 6 to 10 seconds) |

**Why Gemini:** it has a free tier, which suits a project like this. The model name is set in the `.env` file, so it can be changed to Claude or OpenAI without changing the pipeline.

## How the AI part works
- **Policies:** the BookLeaf rules are stored in `backend/app/ai/knowledge_base.py`, split by topic. For each ticket, only the topic that matches its category is sent to the AI. This keeps cost low.
- **Real data:** the author's own book numbers are added to the prompt, so replies have real figures instead of general words. Maths like the next payout date and the ₹1,000 minimum is done in normal code, not by the AI.
- **Tone:** the prompt tells the AI to be kind, say sorry when BookLeaf is at fault, give a clear timeline and end with a next step.
- **Saving cost:** one AI call gives both category and priority, long tickets are cut short, only the last 2 messages are used, and each draft is saved so it is never paid for twice. Every AI call is logged.
- **If the AI fails:** the ticket is still created. Simple keyword rules set the category and priority, and the admin can write the reply by hand or click "Regenerate".
- **Safety:** the ticket text is treated as plain data, not as instructions, so an author cannot trick the AI. The AI is only given data of the author who wrote the ticket.
- **AI never decides alone:** the original AI suggestion is stored next to the final choice, so we can see how often the admin changes it.

## Security
- The API key is only in the backend `.env` file. It is never in the frontend or in Git.
- Passwords are hashed. Every route needs a login token.
- Authors can only see their own books and tickets. Admin pages are blocked for authors.
- Wrong input gives a clear error message, not a crash.

## How to run it on your computer

You need Python, Node.js and PostgreSQL.

1. Create an empty PostgreSQL database named `BookLeaf`.
2. Backend:
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env         # Mac/Linux: cp .env.example .env
```
3. Open `backend/.env` and fill in:
   - `DATABASE_URL` with your database password
   - `JWT_SECRET` with any long random text
   - `GEMINI_API_KEY` with a free key from aistudio.google.com (the app still works without it, using keyword rules)
4. Load the sample data and start the server:
```bash
python scripts/seed.py
uvicorn app.main:app --reload
```
API docs open at http://localhost:8000/docs
5. Frontend (new terminal):
```bash
cd frontend
copy .env.example .env
npm install
npm run dev
```
Open http://localhost:3000

**Logins** (created from the sample data, there is no signup)
- Author: `priya.sharma@email.com` / `Author@123` (all 10 authors use this password)
- Admin: `admin@bookleaf.com` / `Admin@123`

To run the tests: `cd backend && pytest`

## API endpoints
All routes need a login token, except login and health. Full interactive docs are at `/docs`.

| Method | Endpoint | Who | What it does |
|---|---|---|---|
| POST | `/api/auth/login` | Anyone | Log in |
| GET | `/api/books` | Author | My books |
| POST | `/api/tickets` | Author | Create a ticket |
| GET | `/api/tickets` | Author | My tickets and replies |
| GET | `/api/tickets/{id}` | Author | One of my tickets |
| GET | `/api/admin/tickets` | Admin | Ticket queue with filters |
| GET | `/api/admin/tickets/{id}` | Admin | Ticket details and AI draft |
| PATCH | `/api/admin/tickets/{id}` | Admin | Change status, category, priority |
| POST | `/api/admin/tickets/{id}/assign-me` | Admin | Assign to myself |
| POST | `/api/admin/tickets/{id}/reply` | Admin | Send reply to author |
| POST | `/api/admin/tickets/{id}/notes` | Admin | Add private note |
| POST | `/api/admin/tickets/{id}/draft/regenerate` | Admin | Get a new AI draft |
| GET | `/api/admin/stats` | Admin | AI accuracy and usage |

Errors always look the same: `{ "error": { "code": "...", "message": "..." } }`

## What is not done yet (and what I would do next)
- **File attachment:** only the file name is saved. The file is not uploaded.
- **No signup:** only the seeded users can log in.
- **Authors cannot reply inside a ticket:** a follow-up needs a new ticket.
- **AI work runs inside the server:** if the server restarts at the wrong moment, a ticket can miss its draft. A job queue would fix this.
- **Rate limit and caching are in memory:** a real deployment would use Redis.
- **Database tables are made automatically:** a real deployment would use migrations (Alembic).
- **Login token is kept in the browser's local storage:** production should use secure cookies.
- **Polling:** fine for now. Server-Sent Events would be the next step for more users.

## Problems I faced and how I fixed them

**1. Claude to Gemini**
I first built the AI part with Claude Haiku, but it needs paid API credits and I wanted the project to run for free. I moved to Google Gemini's free tier.

**2. First AI draft timed out (504)**
On the deployed app, the first draft failed with `504 DEADLINE_EXCEEDED`. The reason was the 15 second timeout combined with the free server waking up from sleep and the free Gemini tier being slow. Clicking "Regenerate AI draft" worked right away. We can increase the timeout (`AI_TIMEOUT_SECONDS`).

