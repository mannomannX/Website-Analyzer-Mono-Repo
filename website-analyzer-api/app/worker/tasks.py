# app/worker/tasks.py

# Standard-Bibliotheken
import traceback
import random
import json
import asyncio
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse, urlunparse

# Externe Bibliotheken
import requests
from bs4 import BeautifulSoup

# Interne Module und Konfiguration
from app.worker.celery_app import celery_app
from app.db.models import AnalysisJob
from app.core import analyzer, crawler, confidence_scorer, page_classifier, parser
from app.core.config import settings
from app.db.database import init_db

# --- Konfigurationen direkt hier definieren, um Modul-Konflikte zu vermeiden ---
BOILERPLATE_PATH_KEYWORDS = ['datenschutz', 'impressum', 'agb', 'cookie', 'legal', 'login', 'rechtliches']
EXCLUDED_SUBDOMAINS = ['docs', 'api', 'status', 'files', 'developer', 'support']
COLLECTION_SAMPLE_SIZE = 3
COLLECTION_THRESHOLD = 5
CONFIDENCE_THRESHOLD = 60  # Annahme für diesen Wert, kann in 'settings' verschoben werden

def get_clean_root_url(url: str) -> str:
    """Normalisiert eine URL zu ihrer Basis."""
    parsed = urlparse(url)
    netloc = parsed.netloc.replace("www.", "")
    return urlunparse((parsed.scheme, netloc, '', '', '', ''))


async def async_run_analysis(job_id: str, url_input: str):
    """
    Die eigentliche Analyse-Logik, jetzt mit verbesserter Ergebnisverarbeitung.
    """
    await init_db()
    
    print(f"✅✅✅ [WORKER] Async Task für Job {job_id} hat begonnen! ✅✅✅")
    
    job = await AnalysisJob.find_one(AnalysisJob.job_id == job_id)
    if not job:
        print(f"🚨 [{job_id}] Job nicht in der DB gefunden. Breche ab.")
        return

    try:
        job.status = "in_progress"
        await job.save()
        print(f"--- [WORKER] Job {job_id} auf 'in_progress' gesetzt. ---")

        relevant_pages_for_analysis = []
        excluded_pages = []
        failed_page_reports = []

        print(f"--- [WORKER] Job {job_id}: Starte Crawling für {url_input}... ---")
        urls_to_process, link_map, _ = crawler.get_url_list_and_map(url_input)
        if not urls_to_process:
            raise ValueError("Crawling hat keine internen URLs gefunden.")
        print(f"--- [WORKER] Job {job_id}: {len(urls_to_process)} URLs gefunden. ---")
        
        root_url = get_clean_root_url(url_input)

        path_patterns = defaultdict(list)
        for url in urls_to_process:
            path = urlparse(url).path
            pattern_key = "/" + path.split('/')[1] + "/" if len(path.split('/')) > 1 else "/"
            path_patterns[pattern_key].append(url)
        
        sampled_urls = []
        for pattern, urls in path_patterns.items():
            if len(urls) > COLLECTION_THRESHOLD:
                print(f"--- [WORKER] Job {job_id}: Muster '{pattern}' mit {len(urls)} Seiten gefunden. Analysiere Stichprobe. ---")
                sample = random.sample(urls, min(COLLECTION_SAMPLE_SIZE, len(urls)))
                sampled_urls.extend(sample)
                for url in urls:
                    if url not in sample:
                        excluded_pages.append({"url": url, "category": "Redundant", "reason": f"Teil einer Sammlung von {len(urls)} mit Muster '{pattern}'"})
            else:
                sampled_urls.extend(urls)
        urls_to_process = sampled_urls
        print(f"--- [WORKER] Job {job_id}: Nach Sampling verbleiben {len(urls_to_process)} URLs. ---")

        for url in urls_to_process:
            print(f"--- [WORKER] Job {job_id}: Verarbeite Seite {url}... ---")
            try:
                parsed_url = urlparse(url)
                if parsed_url.netloc.split('.')[0].lower() in EXCLUDED_SUBDOMAINS:
                    excluded_pages.append({"url": url, "reason": f"Ausgeschlossene Subdomain", "category": "Irrelevant"})
                    continue

                response = requests.get(url, headers={'User-Agent': settings.CRAWLER_USER_AGENT}, timeout=settings.REQUEST_TIMEOUT)
                response.raise_for_status()
                html = response.text
                
                score = confidence_scorer.calculate_confidence_score(html)
                
                if score >= CONFIDENCE_THRESHOLD:
                    parsed_data = parser.parse_html_to_json(html, url)
                    if "parsing_error" not in parsed_data:
                        parsed_data['parsing_method'] = 'rule_based'
                else:
                    parsed_data = analyzer.parse_with_llm(html, url)
                    if "parsing_error" not in parsed_data:
                        parsed_data['parsing_method'] = 'llm_based'

                if "parsing_error" in parsed_data:
                    failed_page_reports.append(parsed_data)
                else:
                    relevant_pages_for_analysis.append(parsed_data)
            
            except Exception as page_error:
                print(f"--- [WORKER] Job {job_id}: Fehler bei der Verarbeitung der Seite {url}: {page_error} ---")
                failed_page_reports.append({"url": url, "error": f"Seitenverarbeitungsfehler: {str(page_error)}"})

        print(f"--- [WORKER] Job {job_id}: Starte finale Analyse mit {len(relevant_pages_for_analysis)} Seiten. ---")
        final_data_input = {
            "seiten_inhalte": relevant_pages_for_analysis,
            "link_struktur": link_map,
            "parsing_fehlschlaege": failed_page_reports,
            "ausgeschlossene_seiten": excluded_pages
        }
        
        full_llm_response = analyzer.analyze_messaging(final_data_input)
        structured_json_str = analyzer._extract_json_from_text(full_llm_response)
        
        if not structured_json_str:
            raise ValueError("Konnte kein strukturiertes JSON in der KI-Antwort finden.")

        opportunity_analysis_data = json.loads(structured_json_str)

        final_result = {
            "full_text_analysis": full_llm_response,
            "opportunity_analysis": opportunity_analysis_data
        }
        
        job.status = "completed"
        job.result_json = final_result
        job.finished_at = datetime.utcnow()
        await job.save()
        print(f"✅✅✅ [WORKER] Job {job_id} erfolgreich als 'completed' markiert. ✅✅✅")

    except Exception as e:
        print(f"🚨🚨🚨 [{job_id}] Ein kritischer Fehler ist im Task aufgetreten: {e} 🚨🚨🚨")
        error_details = {"error": str(e), "traceback": traceback.format_exc()}
        job.status = "failed"
        job.result_json = error_details
        job.finished_at = datetime.utcnow()
        await job.save()


@celery_app.task(name="run_website_analysis_task")
def run_website_analysis_task(job_id: str, url_input: str):
    """
    Synchrone Wrapper-Funktion, die die async-Logik startet.
    """
    return asyncio.run(async_run_analysis(job_id=job_id, url_input=url_input))