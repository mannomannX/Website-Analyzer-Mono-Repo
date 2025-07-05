# app/db/models.py

from beanie import Document
from pydantic import Field, EmailStr
from typing import Optional
from datetime import datetime

class User(Document):
    email: EmailStr
    hashed_password: str
    role: str = "user"  # Standardrolle ist 'user', kann 'admin' sein
    is_active: bool = True

    class Settings:
        name = "users" # Der Name der Collection in MongoDB


class AnalysisJob(Document):
    url: str
    job_id: str = Field(unique=True)
    status: str = "pending" # pending, in_progress, completed, failed
    result_json: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None

    class Settings:
        name = "analysis_jobs" # Der Name der Collection in MongoDB