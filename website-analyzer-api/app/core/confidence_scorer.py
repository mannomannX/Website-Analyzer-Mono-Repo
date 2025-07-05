# app/core/confidence_scorer.py
from bs4 import BeautifulSoup
import re
# KORREKTUR: Wir importieren nur noch das 'settings'-Objekt
from app.core.config import settings

def _clean_text_for_scoring(text: str) -> str:
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def calculate_confidence_score(html_content: str) -> int:
    if not html_content:
        return 0
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup.find_all(['nav', 'footer', 'header', 'script', 'style', 'aside', 'form']):
        tag.decompose()
    body = soup.body
    if not body:
        return 0

    semantic_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'article', 'section', 'blockquote']
    semantic_count = len(body.find_all(semantic_tags))
    div_count = len(body.find_all('div'))
    semantic_ratio = semantic_count / (div_count + 1)

    all_tags_count = len(body.find_all(True))
    body_text = _clean_text_for_scoring(body.get_text())
    text_length = len(body_text)
    text_to_tag_ratio = text_length / (all_tags_count + 1)
    
    body_size = len(str(body))
    confidence_score = 100

    # KORREKTUR: Alle Aufrufe verwenden jetzt das 'settings'-Objekt
    if semantic_ratio < settings.SCORER_SEMANTIC_RATIO_THRESHOLD_BAD:
        confidence_score -= settings.SCORER_SEMANTIC_RATIO_PENALTY_BAD
    elif semantic_ratio < settings.SCORER_SEMANTIC_RATIO_THRESHOLD_OK:
        confidence_score -= settings.SCORER_SEMANTIC_RATIO_PENALTY_OK
        
    if text_to_tag_ratio < settings.SCORER_TEXT_TO_TAG_RATIO_THRESHOLD_BAD:
        confidence_score -= settings.SCORER_TEXT_TO_TAG_RATIO_PENALTY_BAD
    elif text_to_tag_ratio < settings.SCORER_TEXT_TO_TAG_RATIO_THRESHOLD_OK:
        confidence_score -= settings.SCORER_TEXT_TO_TAG_RATIO_PENALTY_OK
        
    if body_size < settings.SCORER_BODY_SIZE_THRESHOLD_SMALL:
        confidence_score -= settings.SCORER_BODY_SIZE_PENALTY_SMALL
        
    return max(0, confidence_score)