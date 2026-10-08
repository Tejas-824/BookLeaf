from typing import Literal, get_args

Category = Literal[
    "Royalty & Payments",
    "ISBN & Metadata Issues",
    "Printing & Quality",
    "Distribution & Availability",
    "Book Status & Production Updates",
    "General Inquiry",
]
Priority = Literal["Critical", "High", "Medium", "Low"]
Status = Literal["Open", "In Progress", "Resolved", "Closed"]

CATEGORIES = list(get_args(Category))
PRIORITIES = list(get_args(Priority))
STATUSES = list(get_args(Status))

MIN_PAYOUT = 1000          # Rs. minimum payout threshold
OVERDUE_HOURS = 48         # unresolved tickets older than this are flagged