export const CATEGORIES = [
  "Royalty & Payments",
  "ISBN & Metadata Issues",
  "Printing & Quality",
  "Distribution & Availability",
  "Book Status & Production Updates",
  "General Inquiry",
];
export const PRIORITIES = ["Critical", "High", "Medium", "Low"];
export const STATUSES = ["Open", "In Progress", "Resolved", "Closed"];

export const MIN_PAYOUT = 1000; // Rs. minimum payout threshold
export const PAGE_SIZE = 20;

export const EMPTY_FILTERS = {
  status: "",
  category: "",
  priority: "",
  date_from: "",
  date_to: "",
  mine: false,
};