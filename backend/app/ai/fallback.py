from app.core.constants import CATEGORIES

KEYWORDS = {
    "Royalty & Payments": ["royalty", "royalties", "payment", "payout", "paid", "bank", "earning", "refund", "overdue"],
    "ISBN & Metadata Issues": ["isbn", "metadata", "wrong book", "duplicate", "description", "title on"],
    "Printing & Quality": ["print", "quality", "blurry", "misprint", "binding", "damaged", "defect", "reprint"],
    "Distribution & Availability": ["amazon", "flipkart", "unavailable", "not available", "listing", "stock"],
    "Book Status & Production Updates": ["typesetting", "cover design", "proof", "production", "status", "when will"],
}
CRITICAL_WORDS = ["legal", "lawyer", "fraud", "scam", "cheat", "court", "police"]
HIGH_WORDS = ["not received", "haven't received", "have not received", "wrong isbn", "duplicate",
              "unavailable", "defect", "misprint", "urgent", "months"]
LOW_WORDS = ["bio", "update description", "can i change", "how do i", "just wondering"]


def rule_classify(subject: str, description: str) -> tuple[str, str]:
    text = f"{subject} {description}".lower()
    scores = {c: sum(k in text for k in kws) for c, kws in KEYWORDS.items()}
    best = max(scores, key=scores.get)
    category = best if scores[best] > 0 else "General Inquiry"
    assert category in CATEGORIES

    if any(w in text for w in CRITICAL_WORDS):
        priority = "Critical"
    elif any(w in text for w in HIGH_WORDS):
        priority = "High"
    elif any(w in text for w in LOW_WORDS):
        priority = "Low"
    else:
        priority = "Medium"
    return category, priority