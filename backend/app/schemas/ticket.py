from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TicketCreate(BaseModel):
    book_id: str | None = None  # None = General / Account Level
    subject: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10, max_length=5000)
    attachment_name: str | None = Field(default=None, max_length=255)  # UI only

    @field_validator("subject", "description")
    @classmethod
    def strip_text(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be empty")
        return v


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender_role: str
    body: str
    created_at: datetime


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject: str
    description: str
    status: str
    book_id: str | None
    book_title: str | None
    attachment_name: str | None
    created_at: datetime
    updated_at: datetime
    messages: list[MessageOut] = []