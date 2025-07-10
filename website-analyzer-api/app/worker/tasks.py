# app/worker/tasks.py

import traceback
import random
import json
import asyncio
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from urllib.parse import urlparse, urlunparse
import requests

from app.worker.celery_app import celery_app
from app.db.models import AnalysisJob, ExclusionCriterion, DetailedAnalysisCriterion
from app.core import analyzer, crawler, parser
from app.core.config import settings
from app.db.database import init_db
from beanie.operators import In

BOILERPLATE_PATH_KEYWORDS = ['datenschutz', 'impressum', 'agb', 'cookie', 'legal', 'login', 'rechtliches', 'widerrufsbelehrung', 'versand']
EXCLUDED_SUBDOMAINS = ['docs', 'api', 'status', 'files', 'developer', 'support', 'blog', 'karriere', 'jobs']

def get_clean_root_url(url: str) -> str:
    parsed = urlparse(url)
    netloc = parsed.netloc.replace("www.", "")
    return urlunparse((parsed.scheme, netloc, '', '', '', ''))

async def async_run_analysis(job_id: str):
    await init_db()
    
    job = await AnalysisJob.find_one(AnalysisJob.job_id == job_id)
    if not job:
        print(f"🚨🚨🚨 [WORKER][{job_id}] FATAL: Job konnte nicht in der Datenbank gefunden werden. Breche Task ab.")
        return

    job.backend_version = settings.BACKEND_VERSION
    print(f"✅ [WORKER][{job_id}] Task gestartet (Version {job.backend_version}). Setze Status auf 'in_progress'.")
    job.status = "in_progress"
    await job.save()

    try:
        print(f"  [1/5] [{job_id}] Crawling wird gestartet für URL: {job.url}")
        urls_to_process, link_map, crawled_urls = crawler.get_url_list_and_map(job.url)
        if not urls_to_process: raise ValueError("Crawling hat keine internen URLs geliefert.")
        print(f"  [1/5] [{job_id}] Crawling erfolgreich: {len(crawled_urls)} URLs.")

        print(f"  [2/5] [{job_id}] Filtern und Samplen der URL-Liste...")
        page_collections = defaultdict(list)
        for url_str in urls_to_process:
            path_parts = urlparse(url_str).path.strip('/').split('/')
            if len(path_parts) > 1 and not path_parts[1].isdigit(): page_collections[path_parts[0]].append(url_str)
            else: page_collections['root'].append(url_str)
        final_urls_to_parse = []
        excluded_urls_for_report = []
        for key, pages in page_collections.items():
            if len(pages) > settings.COLLECTION_THRESHOLD:
                sample = random.sample(pages, settings.COLLECTION_SAMPLE_SIZE)
                final_urls_to_parse.extend(sample)
                excluded_urls_for_report.extend([p for p in pages if p not in sample])
                print(f"    -> Collection '{key}' gesampelt: {len(sample)} von {len(pages)} Seiten behalten.")
            else:
                final_urls_to_parse.extend(pages)
        print(f"  [2/5] [{job_id}] Filtern abgeschlossen: {len(final_urls_to_parse)} URLs werden geparst.")

        print(f"  [3/5] [{job_id}] Starte Parsing für {len(final_urls_to_parse)} Seiten...")
        relevant_pages_for_analysis = []
        failed_page_reports = []
        for i, url_str in enumerate(final_urls_to_parse):
            try:
                response = requests.get(url_str, timeout=10)
                response.raise_for_status()
                html_content = response.text
                parsed_content = parser.parse_html_to_json(html_content, url_str)
                if parsed_content and not parsed_content.get("parsing_error"):
                    relevant_pages_for_analysis.append(parsed_content)
                else:
                    reason = parsed_content.get("parsing_error", "Parsing lieferte keinen Inhalt.")
                    failed_page_reports.append({"url": url_str, "reason": reason})
            except Exception as e:
                print(f"    -> 🚨 Fehler beim Parsen von {url_str}: {e}")
                failed_page_reports.append({"url": url_str, "reason": str(e)})
        if not relevant_pages_for_analysis: raise ValueError("Parsing lieferte für keine einzige Seite verwertbaren Inhalt.")
        print(f"  [3/5] [{job_id}] Parsing abgeschlossen: {len(relevant_pages_for_analysis)} Seiten erfolgreich verarbeitet.")
        
        print(f"  [4/5] [{job_id}] Bereite Daten für finale KI-Analyse vor...")
        final_data_input = {"seiten_inhalte": relevant_pages_for_analysis, "link_struktur": link_map, "parsing_fehlschlaege": failed_page_reports, "ausgeschlossene_seiten": excluded_urls_for_report}
        print(f"  [4/5] [{job_id}] Sende Anfrage an Google AI. Das kann einen Moment dauern...")
        full_llm_response_str = analyzer.analyze_messaging(final_data_input)
        if not full_llm_response_str: raise ValueError("Die Antwort der KI war leer.")
        print(f"  [4/5] [{job_id}] KI-Analyse erfolgreich abgeschlossen. Antwort erhalten.")

        print(f"  [5/5] [{job_id}] Verarbeite JSON-Antwort der KI...")
        try:
            analysis_data = json.loads(full_llm_response_str)
        except json.JSONDecodeError as e:
            print(f"    -> 🚨 FATAL: KI hat kein valides JSON zurückgegeben! Fehler: {e}")
            print(f"    -> Roh-Antwort der KI:\n---\n{full_llm_response_str}\n---")
            raise ValueError("KI-Antwort konnte nicht als JSON verarbeitet werden.")

        if "error" in analysis_data:
            raise ValueError(f"KI-Analyse hat einen internen Fehler gemeldet: {analysis_data['error']}")

        # Hier werden jetzt ALLE Felder aus der KI-Antwort korrekt gespeichert
        job.opportunity_analysis = analysis_data.get("opportunity_analysis")
        job.full_text_analysis = analysis_data.get("full_text_analysis")
        
        exclusion_data = analysis_data.get("exclusion_analysis", [])
        if exclusion_data:
            job.exclusion_analysis = [ExclusionCriterion(**item) for item in exclusion_data]
            
        detailed_data = analysis_data.get("detailed_analysis", [])
        if detailed_data:
            job.detailed_analysis = [DetailedAnalysisCriterion(**item) for item in detailed_data]

        # *** DIE ENTSCHEIDENDE, NEUE ZEILE ***
        job.actionable_recommendations = analysis_data.get("actionable_recommendations")

        job.status = "completed"
        job.finished_at = datetime.now(timezone.utc)
        await job.save()
        print(f"✅✅✅ [WORKER][{job_id}] Job erfolgreich abgeschlossen und als 'completed' markiert! ✅✅✅")

    except Exception as e:
        full_traceback = traceback.format_exc()
        user_friendly_error_message = f"Analyse fehlgeschlagen: {e}"
        print(f"🚨🚨🚨 [WORKER][{job_id}] KRITISCHER FEHLER IM TASK! 🚨🚨🚨")
        print(f"FEHLERMELDUNG: {user_friendly_error_message}")
        print("--- VOLLSTÄNDIGER TRACEBACK ---")
        print(full_traceback)
        print("-------------------------------")
        job.status = "failed"
        job.error_message = user_friendly_error_message
        job.full_text_analysis = f"DEBUG-INFORMATION:\n\n{full_traceback}"
        job.finished_at = datetime.now(timezone.utc)
        await job.save()
        print(f"🚨 [WORKER][{job_id}] Job-Status wurde auf 'failed' gesetzt und Fehlerdetails gespeichert.")

@celery_app.task(name="run_website_analysis_task")
def run_website_analysis_task(job_id: str):
    try:
        asyncio.run(async_run_analysis(job_id=job_id))
    except Exception as e:
        print(f"🚨🚨🚨 [CELERY WRAPPER][{job_id}] Kritischer Fehler: {e} 🚨🚨🚨")
        async def mark_as_failed():
            await init_db()
            job = await AnalysisJob.find_one(AnalysisJob.job_id == job_id)
            if job and job.status != "failed":
                job.status = "failed"; job.error_message = "Unerwarteter Fehler im Worker-Wrapper."; job.finished_at = datetime.now(timezone.utc); await job.save()
        asyncio.run(mark_as_failed())

# === Der neue, intelligente System-Manager (ersetzt den alten Hausmeister) ===

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Richtet den periodischen System-Manager-Task ein."""
    sender.add_periodic_task(300.0, system_manager_task.s(), name='system manager every 5 mins')

async def _run_system_manager_logic():
    """Die asynchrone Logik für den System-Manager."""
    await init_db()
    now = datetime.now(timezone.utc)
    print(f"--- ⚙️ System-Manager: Starte Überprüfung um {now.isoformat()} ---")

    stale_time_limit = now - timedelta(minutes=5)
    stuck_jobs = await AnalysisJob.find(
        AnalysisJob.created_at < stale_time_limit,
        In(AnalysisJob.status, ["in_progress", "pending"])
    ).to_list()

    for job in stuck_jobs:
        if job.retry_count == 0:
            job.retry_count += 1
            job.notes = (job.notes or "") + f"\n[System-Manager: Task schien blockiert, starte Versuch {job.retry_count}...]"
            await job.save()
            celery_app.send_task('run_website_analysis_task', args=[job.job_id])
            print(f"--- ⚙️ System-Manager: Task {job.job_id} schien blockiert. Wird erneut versucht (Versuch #{job.retry_count}). ---")
        else:
            job.status = "failed"
            job.error_message = "Analyse nach mehreren automatischen Wiederholungsversuchen fehlgeschlagen."
            job.finished_at = now
            await job.save()
            print(f"--- ⚙️ System-Manager: Task {job.job_id} nach Wiederholung endgültig als fehlgeschlagen markiert. ---")

    cleanup_time_limit = now - timedelta(hours=24)
    old_failed_jobs = await AnalysisJob.find(
        AnalysisJob.finished_at < cleanup_time_limit,
        AnalysisJob.status == "failed"
    ).to_list()

    if old_failed_jobs:
        deleted_count = len(old_failed_jobs)
        for job in old_failed_jobs:
            await job.delete()
        print(f"--- ⚙️ System-Manager: {deleted_count} alte, fehlgeschlagene Jobs (>24h) endgültig gelöscht. ---")

    print(f"--- ⚙️ System-Manager: Überprüfung abgeschlossen. ---")
    return f"Checked: {len(stuck_jobs)} stuck, Deleted: {len(old_failed_jobs) if old_failed_jobs else 0} old failed."

@celery_app.task(name="system_manager_task")
def system_manager_task():
    """Synchroner Wrapper für den System-Manager-Task."""
    return asyncio.run(_run_system_manager_logic())