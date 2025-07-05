# app/core/parser.py
import re
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional

def _log_parser_error(url: str, html_content: str, error: str):
    with open("parser_error_log.txt", "a", encoding="utf-8") as f:
        f.write("="*80 + "\n")
        f.write(f"Fehler beim Parsen von URL: {url}\n")
        f.write(f"Fehlermeldung: {error}\n\n")
        f.write(html_content[:5000] + "...\n")
        f.write("="*80 + "\n\n")

def _clean_text(text: str) -> str:
    if not text: return ""
    return re.sub(r'\s+', ' ', text).strip()

def parse_html_to_json(html_content: str, url: str) -> Dict[str, Any]:
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        for tag in soup.find_all(['nav', 'footer', 'header', 'script', 'style', 'aside', 'form']):
            tag.decompose()
        page_title = _clean_text(soup.title.string if soup.title else "")
        h1 = _clean_text(soup.h1.string if soup.h1 else "")
        meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
        meta_description = _clean_text(meta_desc_tag.get('content', '') if meta_desc_tag else "")
        page_data = {"url": url, "page_title": page_title, "meta_description": meta_description, "h1": h1, "intro_content": [], "content_structure": []}
        main_content = soup.main if soup.main else soup.body
        if not main_content: return page_data
        content_structure: List[Dict[str, Any]] = []
        current_section: Optional[Dict[str, Any]] = None
        has_seen_h2 = False
        relevant_tags = main_content.find_all(['h2', 'h3', 'p', 'ul', 'ol', 'blockquote'])
        for tag in relevant_tags:
            if tag.name == 'h2':
                has_seen_h2 = True
                if current_section: content_structure.append(current_section)
                current_section = {"heading": _clean_text(tag.get_text()), "content_blocks": []}
                continue
            if not has_seen_h2:
                intro_text = _clean_text(tag.get_text())
                if intro_text: page_data["intro_content"].append(intro_text)
                continue
            if not current_section: current_section = {"heading": "", "content_blocks": []}
            if tag.name in ('p', 'blockquote'):
                text = _clean_text(tag.get_text())
                if text: current_section["content_blocks"].append({"type": "paragraph", "text": text})
            elif tag.name in ('ul', 'ol'):
                items = [_clean_text(li.get_text()) for li in tag.find_all('li') if _clean_text(li.get_text())]
                if items: current_section["content_blocks"].append({"type": "list", "items": items})
            elif tag.name == 'h3':
                text = _clean_text(tag.get_text())
                if text: current_section["content_blocks"].append({"type": "subheading", "text": text})
        if current_section and current_section["content_blocks"]:
            content_structure.append(current_section)
        page_data["content_structure"] = content_structure
        return page_data
    except Exception as e:
        error_message = f"Rule-based parser failed unexpectedly: {e}"
        _log_parser_error(url, html_content, error_message)
        return {"url": url, "parsing_error": error_message}