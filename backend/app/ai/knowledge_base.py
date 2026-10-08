# KB is plain Python data, loaded once when the server starts.

COMPANY = (
    "BookLeaf Publishing is a self-publishing company in India and the US. "
    "Packages: Standard Free (no upfront cost) and Bestseller Breakthrough (paid, with marketing "
    "and distribution add-ons). We handle cover design, typesetting, ISBN, printing, distribution "
    "and royalty management. In-house printing and warehouse are in Delhi. Print partners: "
    "Repro India and Epitome Books."
)

SECTIONS = {
    "royalty": (
        "ROYALTY POLICY:\n"
        "- 80/20 split: 80% of net profit per book to the author, 20% to BookLeaf.\n"
        "- Net profit = MRP minus printing cost, platform commission (Amazon/Flipkart) and shipping.\n"
        "- Royalties are calculated quarterly and paid within 45 days of the quarter ending.\n"
        "- Minimum payout is Rs. 1,000. Below that, the amount rolls over to the next quarter.\n"
        "- Payout is by bank transfer to the account linked in the author dashboard.\n"
        "- The dashboard shows a detailed royalty breakdown with sales per platform.\n"
        "EXAMPLES:\n"
        "- 'No royalty after 4 months': acknowledge frustration, explain quarterly cycle and 45-day "
        "window, ask them to check bank details are linked, give the next payout date. If really "
        "overdue, escalate with a 48-hour resolution timeline.\n"
        "- 'Royalty seems too low': explain the net profit calculation, offer a line-by-line "
        "royalty breakdown, do not be defensive."
    ),
    "isbn": (
        "ISBN POLICY:\n"
        "- Every book gets a unique ISBN assigned by BookLeaf under BookLeaf's publisher imprint.\n"
        "- If an author wants an ISBN under their own imprint, they must obtain it independently.\n"
        "- ISBN errors (duplicate, wrong book linked) are HIGH priority and escalated to the "
        "production team.\n"
        "EXAMPLE: 'Different ISBN on Amazon vs physical copy': treat as high priority, say it is a "
        "serious data issue, confirm escalation to production team now, give a 48-hour timeline."
    ),
    "printing": (
        "PRINTING & QUALITY:\n"
        "- In-house printing handles most orders. Overflow or special formats go to Repro India or "
        "Epitome Books.\n"
        "- Standard print turnaround is 5-7 business days from order confirmation.\n"
        "- For quality issues (misprints, binding defects, colour problems) BookLeaf arranges a "
        "free reprint after verification. The author may need to share photos of the defective copy.\n"
        "EXAMPLE: 'Blurry images, misaligned pages': apologise sincerely, ask for photos, confirm a "
        "free reprint once verified, give 5-7 business days for the reprint."
    ),
    "distribution": (
        "DISTRIBUTION & AVAILABILITY:\n"
        "- Books are listed on Amazon India, Flipkart, Amazon US, Amazon UK and the BookLeaf Store.\n"
        "- New listings go live within 7-10 business days after publication is complete.\n"
        "- 'Unavailable' on a platform usually means a stock sync issue. The team can trigger a "
        "re-sync within 24-48 hours.\n"
        "EXAMPLE: 'Showing Currently Unavailable on Amazon': explain it is typically a stock sync "
        "issue, confirm you are triggering a re-sync, set expectation of 24-48 hours."
    ),
    "production": (
        "PRODUCTION STAGES:\n"
        "Manuscript Received -> Editing (if opted) -> Cover Design -> Typesetting -> Proofreading -> "
        "ISBN Assignment -> Printing -> Distribution Setup -> Published & Live.\n"
        "- Authors get an email at each stage.\n"
        "- Delays usually happen at Cover Design (waiting for author approval) and Proofreading "
        "(revision rounds).\n"
        "EXAMPLE: 'Still in typesetting after 3 weeks': check the real status, be honest about the "
        "reason (for example waiting on author approval) without blaming the author, give a specific "
        "updated timeline, frame it collaboratively."
    ),
    "general": (
        "GENERAL:\n"
        "- Metadata updates (for example a book description on Amazon) can be submitted through the "
        "dashboard or by emailing the BookLeaf team. Changes usually show on platforms in 3-5 "
        "business days."
    ),
}

# Which sections each category needs
CATEGORY_SECTIONS = {
    "Royalty & Payments": ["royalty"],
    "ISBN & Metadata Issues": ["isbn", "general"],
    "Printing & Quality": ["printing"],
    "Distribution & Availability": ["distribution"],
    "Book Status & Production Updates": ["production"],
    "General Inquiry": ["general", "royalty", "distribution"],
}


def get_kb_context(category: str) -> str:
    keys = CATEGORY_SECTIONS.get(category, ["general"])
    parts = [COMPANY] + [SECTIONS[k] for k in keys]
    return "\n\n".join(parts)