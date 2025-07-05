# app/core/page_classifier.py
import google.generativeai as genai
import json
from typing import Dict, Any

from app.core.config import settings

def classify_page(page_data: Dict[str, Any]) -> str:
    if not settings.DEIN_GOOGLE_API_KEY or "IHR_GOOGLE_API_KEY" in settings.DEIN_GOOGLE_API_KEY:
        return "Hard_to_read"
    
    classification_input = {
        "url": page_data.get("url", ""),
        "page_title": page_data.get("page_title", ""),
        "meta_description": page_data.get("meta_description", ""),
        "h1": page_data.get("h1", ""),
        "headings_in_content": [section.get("heading") for section in page_data.get("content_structure", []) if section.get("heading")]
    }

    try:
        genai.configure(api_key=settings.DEIN_GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        data_as_json_string = json.dumps(classification_input, indent=2, ensure_ascii=False)
        
        # KORREKTUR: Greift auf den Prompt aus dem settings-Objekt zu
        prompt = settings.PAGE_CLASSIFIER_PROMPT.format(page_json_data=data_as_json_string)
        
        response = model.generate_content(prompt)
        category = response.text.strip()
        
        allowed_categories = ['Core_Messaging', 'Supporting_Content', 'Boilerplate', 'Hard_to_read']
        if category in allowed_categories:
            return category
        else:
            return "Hard_to_read"
            
    except Exception as e:
        print(f"Fehler im 'page_classifier' für URL {page_data.get('url', 'Unbekannt')}: {e}")
        return "Hard_to_read"