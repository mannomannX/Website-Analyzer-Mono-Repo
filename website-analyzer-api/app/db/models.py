# app/db/models.py

from beanie import Document
from pydantic import Field, EmailStr, BaseModel
from typing import Optional, List, Any, Dict, Union 
from datetime import datetime

class User(Document):
    email: EmailStr
    hashed_password: str
    # KORREKTUR: Das von der Authentifizierung (dependencies.py) benötigte Feld
    # wird wieder hinzugefügt, um den 'AttributeError' zu beheben.
    is_active: bool = True 
    class Settings:
        name = "users"

# --- Der Rest der Datei bleibt exakt so, wie du ihn hast ---
class ExclusionCriterion(BaseModel):
    criterion: str
    triggered: bool
    justification: Optional[str] = None

class DetailedAnalysisCriterion(BaseModel):
    criterion: str
    score: int
    reasoning: str
    evidence_quote: Optional[str] = None

class AnalysisJob(Document):
    url: str
    job_id: str = Field(unique=True)
    status: str = "pending"
    
    opportunity_analysis: Optional[Dict[str, Any]] = None
    full_text_analysis: Optional[str] = None
    exclusion_analysis: Optional[List[ExclusionCriterion]] = None
    detailed_analysis: Optional[List[DetailedAnalysisCriterion]] = None
    actionable_recommendations: Optional[List[Union[str, Dict[str, Any]]]] = None
    
    notes: Optional[str] = None
    retry_count: int = Field(default=0)
    backend_version: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    user_id: Optional[str] = None
    error_message: Optional[str] = None

    class Settings: name = "analysis_jobs"