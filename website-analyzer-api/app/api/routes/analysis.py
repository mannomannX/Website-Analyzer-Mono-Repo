# app/api/routes/analysis.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, List
import uuid

from app.db.models import User, AnalysisJob
from app.api.dependencies import get_current_user
from app.schemas.analysis import AnalysisCreate, JobResponse, AnalysisResult
from app.worker.tasks import run_website_analysis_task

router = APIRouter()

@router.post("/analyze", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_analysis(
    analysis_in: AnalysisCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Nimmt eine URL entgegen, erstellt einen Analyse-Job und startet
    den Hintergrund-Task.
    """
    job_id = str(uuid.uuid4())
    url = str(analysis_in.url)
    
    print(f"--- [API] Neuer Analyse-Auftrag erhalten für URL: {url} ---")
    
    analysis_job = AnalysisJob(
        url=url,
        job_id=job_id,
        status="pending",
    )
    await analysis_job.insert()
    print(f"--- [API] Job {job_id} in DB mit Status 'pending' erstellt. ---")
    
    # Startet den Hintergrund-Task
    try:
        run_website_analysis_task.delay(job_id=job_id, url_input=url)
        print(f"--- [API] Task für Job {job_id} erfolgreich an Celery übergeben. ---")
    except Exception as e:
        print(f"🚨🚨🚨 [API] FEHLER BEIM AUFRUF VON .delay()! Task konnte nicht an Celery übergeben werden: {e} 🚨🚨🚨")
        raise HTTPException(status_code=500, detail="Could not enqueue a new analysis task.")

    return {"job_id": job_id, "status": "accepted", "url": url}


@router.get("/status/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Gibt den Status eines bestimmten Analyse-Jobs zurück.
    """
    job = await AnalysisJob.find_one(AnalysisJob.job_id == job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    print(f"--- [API] Status für Job {job_id} abgefragt. Aktueller Status: {job.status} ---")
    
    return {"job_id": job.job_id, "status": job.status, "url": job.url}


@router.get("/results/{job_id}", response_model=AnalysisResult)
async def get_analysis_results(
    job_id: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Gibt das vollständige Ergebnis eines abgeschlossenen Analyse-Jobs zurück.
    """
    job = await AnalysisJob.find_one(AnalysisJob.job_id == job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "completed":
        raise HTTPException(status_code=400, detail=f"Job status is '{job.status}', not 'completed'.")
        
    return job.result_json


# NEU: Ein Endpunkt, um den gesamten Analyse-Verlauf abzurufen
@router.get("/history", response_model=List[AnalysisResult])
async def get_analysis_history(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Gibt eine Liste aller Analyse-Jobs zurück, sortiert nach Erstellungsdatum.
    """
    # Holt alle Jobs aus der DB, sortiert nach dem neuesten Datum
    jobs = await AnalysisJob.find_all().sort(-AnalysisJob.created_at).to_list()
    return jobs