# BookLeaf Author Support Portal

This is a web app where BookLeaf authors can raise support tickets, and the support team can answer them faster. AI writes the first draft of the reply, but a person always checks it before it goes to the author.

## What it does

**For authors**
- Log in and see your own books: ISBN, copies sold, and how much royalty is earned, paid and pending.
- Raise a ticket about a book, or about your account in general.
- See your tickets, their status and the team's replies. New replies show up by themselves, no need to refresh the page.

**For the support team (admin)**
- See all tickets in one list. You can filter by status, category, priority and date. Urgent and old tickets are easy to spot.
- AI picks the category and the priority. The admin can change both.
- AI writes a draft reply using BookLeaf's rules and the author's real numbers. The admin edits it and sends it.
- Change the ticket status, add private notes (authors never see these), and assign a ticket to yourself.
- A stats page shows how often the team keeps the AI's suggestions and how many AI calls were made.

## How a ticket moves
1. The author submits a ticket. It is saved first, so it is never lost.
2. In the background, AI picks a category and priority, then writes a draft reply.
3. The admin opens the ticket and the draft is already there. They edit it and send it.
4. The author sees the reply within a few seconds.

## Tech used
| Part | Tool |
|---|---|
| Frontend | Next.js (React) |
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| AI | Google Gemini |
| Live updates | Polling (the page checks for new data every 6 to 10 seconds) |

**Why Gemini:** it has a free tier, so it suits a project like this. The model name is set in the `.env` file, so I can switch to Claude or OpenAI later without changing the rest of the code.

## How the AI part works
- **Company rules:** BookLeaf's policies are saved in `backend/app/ai/knowledge_base.py`, split by topic. For each ticket, only the topic that matches its category is sent to the AI. This keeps the cost low.
- **Real data:** the author's own book numbers go into the prompt, so replies have real figures and not vague words. Calculations like the next payout date and the ₹1,000 minimum are done in normal code, not by the AI.
- **Tone:** the AI is told to be kind, say sorry when BookLeaf is at fault, give a clear timeline, and end with a next step.
- **Saving cost:** one AI call gives both category and priority. Very long tickets are cut short. Only the last 2 messages are used. Each draft is saved, so we never pay for it twice. Every AI call is logged.
- **If the AI fails:** the ticket is still created. Simple keyword rules set the category and priority, and the admin can write the reply by hand or click "Regenerate".
- **Safety:** the ticket text is treated as plain data, not as instructions, so an author cannot trick the AI. The AI only sees the data of the author who wrote the ticket.
- **AI never decides alone:** the AI's first suggestion is saved next to the final choice, so we can see how often the admin changes it.

## Extra things I added

- **No double tickets:** if an author clicks Submit twice, only one ticket is created.
- **Ticket limit:** an author can submit 10 tickets per hour. This stops spam and keeps AI cost low.
- **Backup when AI is down:** keyword rules still set the category and priority, so a ticket never stays unsorted.
- **"AI is not sure" warning:** if the AI is unsure about a ticket, the admin sees a warning to check it carefully.
- **Labels on AI values:** the admin can see if a category came from the AI, from the keyword rules, or from a person.
- **AI accuracy tracking:** the stats page shows how often the team agrees with the AI.
- **AI usage log:** every AI call is saved with its time, size and result, so cost and failures are easy to check.
- **Change history:** every status, category, priority, reply and note change is saved with who did it and when.
- **Overdue tickets stand out:** open tickets older than 48 hours get a badge, and critical ones get a red mark.
- **Regenerate button:** if a draft is bad or the AI failed, the admin can ask for a new one.

## Security
- The API key is only in the backend `.env` file. It is never in the frontend or in Git.
- Passwords are hashed, and every route needs a login token.
- Authors can only see their own books and tickets. Admin pages are blocked for authors.
- If the input is wrong, the user gets a clear error message instead of a crash.

## How to run it on your computer

You need Python, Node.js and PostgreSQL.

1. Create an empty PostgreSQL database named `BookLeaf`.
2. Set up the backend:
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
   - `GEMINI_API_KEY` with a free key from aistudio.google.com (the app still works without it, using the keyword rules)
4. Load the sample data and start the server:
```bash
python scripts/seed.py
uvicorn app.main:app --reload
```
The API docs open at http://localhost:8000/docs
5. Set up the frontend (in a new terminal):
```bash
cd frontend
copy .env.example .env
npm install
npm run dev
```
Open http://localhost:3000

**Logins** (made from the sample data, there is no signup)
- Author: `priya.sharma@email.com` / `Author@123` (all 10 authors use this password)
- Admin: `admin@bookleaf.com` / `Admin@123`

## API endpoints
Every route needs a login token, except login and health. Full interactive docs are at `/docs`.

| Method | Endpoint | Who | What it does |
|---|---|---|---|
| POST | `/api/auth/login` | Anyone | Log in |
| GET | `/api/books` | Author | My books |
| POST | `/api/tickets` | Author | Create a ticket |
| GET | `/api/tickets` | Author | My tickets and replies |
| GET | `/api/tickets/{id}` | Author | One of my tickets |
| GET | `/api/admin/tickets` | Admin | Ticket list with filters |
| GET | `/api/admin/tickets/{id}` | Admin | Ticket details and AI draft |
| PATCH | `/api/admin/tickets/{id}` | Admin | Change status, category, priority |
| POST | `/api/admin/tickets/{id}/assign-me` | Admin | Assign to myself |
| POST | `/api/admin/tickets/{id}/reply` | Admin | Send reply to author |
| POST | `/api/admin/tickets/{id}/notes` | Admin | Add private note |
| POST | `/api/admin/tickets/{id}/draft/regenerate` | Admin | Get a new AI draft |
| GET | `/api/admin/stats` | Admin | AI accuracy and usage |

All errors look the same: `{ "error": { "code": "...", "message": "..." } }`

## What is not done yet (and what I would do next)
- **File attachment:** only the file name is saved. The file itself is not uploaded.
- **No signup:** only the seeded users can log in.
- **Authors cannot reply inside a ticket:** for a follow-up they need to create a new ticket.
- **AI runs inside the server:** if the server restarts at the wrong moment, a ticket can miss its draft. A job queue would fix this.
- **Rate limit and caching are kept in memory:** a real deployment would use Redis.
- **Database tables are created automatically:** a real deployment would use migrations (Alembic).
- **Login token is stored in the browser's local storage:** production should use secure cookies.
- **Polling:** fine for now. Server-Sent Events would be better for more users.

## Problems I faced and how I fixed them

**1. Moving from Claude to Gemini**
I first built the AI part with Claude Haiku, but it needs paid credits and I wanted the project to run for free. So I moved to Google Gemini's free tier.

**2. The first AI draft timed out (504)**
On the deployed app, the first draft failed with a `504 DEADLINE_EXCEEDED` error. The reasons were the 15 second timeout, the free server waking up from sleep, and the free Gemini tier being slow. Clicking "Regenerate AI draft" worked right away. The timeout can be increased with `AI_TIMEOUT_SECONDS`.

**3. Database connection errors**
My local database password has an `@` in it, which broke the connection URL. I fixed it by writing it as `%40`. I also found out that PostgreSQL treats `BookLeaf` and `bookleaf` as two different database names.