from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ResearchRequest(BaseModel):
    question: str = Field(min_length=10, max_length=2000)


class SourcePublic(BaseModel):
    id: str
    question: str
    title: str
    url: str
    content: str
    score: float | None = None
    credibility_label: str = "Unknown"
    credibility_score: float = 0.3

    model_config = ConfigDict(from_attributes=True)


class ResearchResponse(BaseModel):
    id: str
    question: str
    status: str
    answer: str | None
    sub_questions: list[str]
    sources: list[SourcePublic]
    contradictions: list[str]
    gaps: list[str]
    iterations: int
    created_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class HistoryItem(BaseModel):
    id: str
    question: str
    status: str
    iterations: int
    created_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
