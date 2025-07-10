# app/api/routes/analysis.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, List, Optional
import uuid
import re
from datetime import datetime, timedelta 
from collections import Counter
from app.core.config import settings
from pydantic import BaseModel

from app.db.models import User, AnalysisJob
from app.api.dependencies import get_current_user
# Wir verwenden die bereits existierenden Schemas für Konsistenz
from app.schemas.analysis import JobResponse, AnalysisCreate 
from app.worker.celery_app import celery_app 

router = APIRouter()

# Wir verwenden hier AnalysisCreate, das bereits 'url' und 'notes' enthalten sollte.
# Falls nicht, müssen wir dieses Schema anpassen.
@router.post("/analyze", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_analysis(
    analysis_in: AnalysisCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Nimmt eine URL entgegen, erstellt einen Analyse-Job und startet den Task.
    """
    job_id = str(uuid.uuid4())
    url = str(analysis_in.url)
    
    print(f"--- [API] Neuer Analyse-Auftrag für URL: {url} von User: {current_user.id} ---")
    
    analysis_job = AnalysisJob(
        url=url,
        job_id=job_id,
        status="pending",
        notes=analysis_in.notes if hasattr(analysis_in, 'notes') else None,
        user_id=str(current_user.id),
        # NEU: Wir stempeln den Job mit der aktuellen Backend-Version aus der Config
        backend_version=settings.BACKEND_VERSION
    )
    await analysis_job.insert()
    
    celery_app.send_task('run_website_analysis_task', args=[job_id])
    
    return {"job_id": job_id, "status": "accepted", "url": url}


@router.get("/status/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str, current_user: User = Depends(get_current_user)) -> Any:
    """ Gibt den Status eines bestimmten Analyse-Jobs zurück. """
    job = await AnalysisJob.find_one(AnalysisJob.job_id == job_id, AnalysisJob.user_id == str(current_user.id))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job.job_id, "status": job.status, "url": job.url}


@router.get("/results/{job_id}", response_model=AnalysisJob)
async def get_analysis_results(job_id: str, current_user: User = Depends(get_current_user)) -> Any:
    """ Gibt das vollständige Ergebnis eines abgeschlossenen Analyse-Jobs zurück. """
    job = await AnalysisJob.find_one(AnalysisJob.job_id == job_id, AnalysisJob.user_id == str(current_user.id))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status not in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail=f"Job status is '{job.status}', not 'completed' or 'failed'.")
    return job


@router.get("/history", response_model=List[AnalysisJob])
async def get_analysis_history(current_user: User = Depends(get_current_user)) -> Any:
    """ Gibt die gesamte Analyse-Historie für den eingeloggten Benutzer zurück. """
    jobs = await AnalysisJob.find(AnalysisJob.user_id == str(current_user.id)).sort(-AnalysisJob.created_at).to_list()
    return jobs


@router.get("/check")
async def check_domain_history(domain: str, current_user: User = Depends(get_current_user)):
    """
    Prüft, ob eine Domain bereits analysiert wurde und gibt den letzten Job zurück.
    """
    escaped_domain = re.escape(domain)
    domain_regex = f"https?://(www\\.)?{escaped_domain}"
    
    latest_job = await AnalysisJob.find(
        {"url": {"$regex": domain_regex, "$options": "i"}},
        AnalysisJob.user_id == str(current_user.id)
    ).sort(-AnalysisJob.created_at).limit(1).first_or_none()

    if latest_job:
        triggered_by_user = await User.get(latest_job.user_id)
        triggered_by_email = triggered_by_user.email if triggered_by_user else "Unbekannt"
        
        return {
            "exists": True,
            "last_analyzed_at": latest_job.created_at,
            "job_id": latest_job.job_id,
            "status": latest_job.status,
            "triggered_by": triggered_by_email
        }
    return {"exists": False}


@router.post("/cleanup", status_code=202, summary="Trigger Stale Task Cleanup")
async def trigger_cleanup(current_user: User = Depends(get_current_user)):
    """
    Löst den Aufräum-Task für veraltete Analysen manuell aus.
    """
    task = celery_app.send_task('system_manager_task', args=[])
    return {"message": "Cleanup task triggered successfully.", "task_id": task.id}


# NEU: Endpunkt zum Löschen einer Analyse
@router.delete("/{job_id}", status_code=204, summary="Delete an Analysis Job")
async def delete_analysis(job_id: str, current_user: User = Depends(get_current_user)):
    """
    Löscht einen Analyse-Job aus der Datenbank.
    Stellt sicher, dass nur der Besitzer des Jobs ihn löschen kann.
    """
    # Wir suchen den Job anhand der job_id UND der user_id, um sicherzustellen,
    # dass Nutzer nur ihre eigenen Analysen löschen können.
    job = await AnalysisJob.find_one(AnalysisJob.job_id == job_id, AnalysisJob.user_id == str(current_user.id))
    
    if not job:
        raise HTTPException(status_code=404, detail="Analyse-Job nicht gefunden oder keine Berechtigung zum Löschen.")
    
    await job.delete()
    
    # Bei Erfolg gibt man bei DELETE üblicherweise keinen Body zurück.
    # Der Status-Code 204 "No Content" signalisiert den Erfolg.
    return None

# NEU: Endpunkt, um eine Analyse erneut zu starten
@router.post("/{job_id}/rerun", response_model=JobResponse, status_code=202, summary="Rerun an Analysis Job")
async def rerun_analysis(job_id: str, current_user: User = Depends(get_current_user)):
    """
    Findet einen alten Analyse-Job und startet einen neuen Job mit der gleichen URL und den gleichen Notizen.
    """
    # Finde den alten Job, um die Daten zu kopieren
    old_job = await AnalysisJob.find_one(AnalysisJob.job_id == job_id, AnalysisJob.user_id == str(current_user.id))
    if not old_job:
        raise HTTPException(status_code=404, detail="Ursprünglicher Analyse-Job nicht gefunden.")

    # Erstelle einen neuen Job, genau wie beim normalen '/analyze'
    new_job_id = str(uuid.uuid4())
    
    analysis_job = AnalysisJob(
        url=old_job.url,
        job_id=new_job_id,
        status="pending",
        notes=old_job.notes, # Übernehme die alten Notizen
        user_id=str(current_user.id)
    )
    await analysis_job.insert()
    
    celery_app.send_task('run_website_analysis_task', args=[new_job_id])
    
    return {"job_id": new_job_id, "status": "accepted", "url": old_job.url}

# ... (andere imports und bestehende Routen)
from datetime import datetime, timedelta
from collections import Counter

# NEU: Endpunkt für die Statistik-Übersicht
@router.get("/stats", summary="Get Analysis Statistics")
async def get_analysis_stats(current_user: User = Depends(get_current_user)):
    """
    Berechnet und liefert Statistiken über die Analysen des aktuellen Nutzers
    für die letzten 30 Tage.
    """
    # Definiere den Zeitrahmen
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Finde alle relevanten Jobs des Nutzers
    jobs_in_period = await AnalysisJob.find(
        AnalysisJob.user_id == str(current_user.id),
        AnalysisJob.created_at >= thirty_days_ago
    ).to_list()

    total_analyses = len(jobs_in_period)
    
    # Zähle die Klassifizierungen der abgeschlossenen Jobs
    classifications = [
        job.opportunity_analysis['classification'] 
        for job in jobs_in_period 
        if job.status == 'completed' and job.opportunity_analysis and 'classification' in job.opportunity_analysis
    ]
    
    classification_counts = Counter(classifications)

    return {
        "total_analyses_last_30_days": total_analyses,
        "classification_breakdown": {
            "IDEAL_PARTNER": classification_counts.get('IDEAL_PARTNER', 0),
            "LOW_URGENCY": classification_counts.get('LOW_URGENCY', 0),
            "HIGH_EFFORT_LOW_FIT": classification_counts.get('HIGH_EFFORT_LOW_FIT', 0),
            "NOT_RELEVANT": classification_counts.get('NOT_RELEVANT', 0),
        }
    }

# Ein simples Pydantic-Modell für den Request-Body des Updates
class NotesUpdateRequest(BaseModel):
    notes: str

# NEU: Endpunkt zum Aktualisieren der Notizen
@router.patch("/{job_id}/notes", response_model=AnalysisJob, summary="Update Notes for an Analysis")
async def update_analysis_notes(
    job_id: str,
    update_request: NotesUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Aktualisiert das Notizfeld für einen spezifischen Analyse-Job.
    """
    job = await AnalysisJob.find_one(AnalysisJob.job_id == job_id, AnalysisJob.user_id == str(current_user.id))
    if not job:
        raise HTTPException(status_code=404, detail="Analyse-Job nicht gefunden.")
    
    job.notes = update_request.notes
    await job.save()
    return job