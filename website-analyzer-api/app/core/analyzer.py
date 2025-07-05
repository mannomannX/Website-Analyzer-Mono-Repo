# app/core/analyzer.py
import json
import re
from typing import Any, Dict, List, Optional
import google.generativeai as genai

from app.core.config import settings

def _log_llm_error(url: str, prompt: str, raw_response: str, error_type: str, details: str):
    with open("llm_error_log.txt", "a", encoding="utf-8") as f:
        f.write("="*80 + "\n")
        f.write(f"Fehler bei URL/Task: {url}\n")
        f.write(f"Fehler-Typ: {error_type}\n")
        f.write(f"Details: {details}\n\n")
        f.write("--- Gesendeter Prompt an die KI ---\n")
        f.write(prompt + "\n\n")
        f.write("--- Rohe Antwort der KI ---\n")
        f.write(raw_response + "\n")
        f.write("="*80 + "\n\n")

def _extract_json_from_text(text: str) -> Optional[str]:
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return None

def parse_with_llm(html_content: str, url: str) -> Dict[str, Any]:
    if not settings.DEIN_GOOGLE_API_KEY or "IHR_GOOGLE_API_KEY" in settings.DEIN_GOOGLE_API_KEY:
        return {"url": url, "parsing_error": "API Key not configured."}
    
    # KORREKTUR: Greift auf den Prompt aus dem settings-Objekt zu
    prompt = settings.LLM_PARSER_PROMPT.format(raw_html_content=html_content)
    raw_response_text = ""
    
    try:
        genai.configure(api_key=settings.DEIN_GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        raw_response_text = response.text
        
        json_string = _extract_json_from_text(raw_response_text)
        
        if not json_string:
            error_message = "LLM-Parser hat kein valides JSON-Objekt zurückgegeben."
            _log_llm_error(url, prompt, raw_response_text, "No JSON Found", error_message)
            return {"url": url, "parsing_error": error_message, "raw_llm_response": raw_response_text}

        parsed_json = json.loads(json_string)
        return parsed_json

    except Exception as e:
        error_message = f"Unerwarteter Fehler im LLM-Parser: {e}"
        _log_llm_error(url, prompt, raw_response_text, "Unexpected Error", error_message)
        return {"url": url, "parsing_error": error_message, "raw_llm_response": raw_response_text}

def analyze_messaging(structured_data: dict) -> str:
    if not settings.DEIN_GOOGLE_API_KEY or "IHR_GOOGLE_API_KEY" in settings.DEIN_GOOGLE_API_KEY:
        return json.dumps({"error": "API Key nicht konfiguriert."})

    if not structured_data.get("seiten_inhalte") and not structured_data.get("parsing_fehlschlaege"):
        return json.dumps({"error": "Keine Daten zum Analysieren vorhanden."})
        
    data_as_json_string = json.dumps(structured_data, indent=2, ensure_ascii=False)
    # KORREKTUR: Greift auf den Prompt aus dem settings-Objekt zu
    prompt = settings.FINAL_ANALYZER_PROMPT.format(structured_website_data=data_as_json_string)
    raw_response_text = ""

    try:
        genai.configure(api_key=settings.DEIN_GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        raw_response_text = response.text
        
        cleaned_response = _extract_json_from_text(raw_response_text)

        if not cleaned_response:
             _log_llm_error("FINALE_ANALYSE", prompt, raw_response_text, "No JSON Found", "Konnte kein valides JSON-Objekt in der finalen Analyse-Antwort finden.")
             return raw_response_text

        return cleaned_response

    except Exception as e:
        error_msg = f"Unerwarteter Fehler in analyze_messaging: {e}"
        _log_llm_error("FINALE_ANALYSE", prompt, raw_response_text, "Unexpected Error", error_msg)
        return f'{{"error": "Bei der finalen Analyse ist ein unerwarteter Fehler aufgetreten.", "details": "{e}"}}'