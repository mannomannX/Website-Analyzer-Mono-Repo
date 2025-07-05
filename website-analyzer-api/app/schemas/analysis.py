# app/schemas/analysis.py

from pydantic import BaseModel, HttpUrl, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class AnalysisCreate(BaseModel):
    url: HttpUrl

class JobResponse(BaseModel):
    job_id: str
    status: str
    url: str

# --- Detaillierte Pydantic-Modelle für das strukturierte Analyse-Ergebnis ---
# KORREKTUR: Alle Felder werden optional, um mit alten/unvollständigen Daten kompatibel zu sein.

class DetailedCriterion(BaseModel):
    name: Optional[str] = None
    score: Optional[int] = Field(None, ge=1, le=10)
    justification: Optional[str] = None

class WorstCriterion(BaseModel):
    name: Optional[str] = None
    evidence_quote: Optional[str] = None

class OpportunityAnalysisData(BaseModel):
    classification: Optional[str] = None
    summary_justification: Optional[str] = None
    pain_score: Optional[int] = Field(None, ge=1, le=10)
    potential_score: Optional[int] = Field(None, ge=1, le=10)
    primary_weakness: Optional[str] = None
    detailed_criteria: Optional[List[DetailedCriterion]] = None
    worst_criterion: Optional[WorstCriterion] = None
    top_recommendation: Optional[str] = None

class FullAnalysisResult(BaseModel):
    full_text_analysis: Optional[str] = None
    opportunity_analysis: Optional[OpportunityAnalysisData] = None

# Schema für den finalen Job, der in der DB gespeichert und an das Frontend gesendet wird
class AnalysisResult(BaseModel):
    url: str
    job_id: str
    status: str
    created_at: datetime
    finished_at: Optional[datetime] = None
    # result_json kann jetzt jede Art von Daten enthalten, wird aber als FullAnalysisResult validiert, wenn vorhanden
    result_json: Optional[Any] = None

    class Config:
        from_attributes = True