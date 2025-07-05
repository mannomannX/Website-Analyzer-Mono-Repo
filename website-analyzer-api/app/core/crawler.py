# app/core/crawler.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from collections import deque

# KORREKTUR: Wir importieren NUR noch das 'settings'-Objekt.
from app.core.config import settings

def get_base_domain(url: str) -> str:
    """Extrahiert die Basis-Domain (z.B. 'google.com') aus einer URL."""
    try:
        parsed_url = urlparse(url)
        domain_parts = parsed_url.netloc.split('.')
        if len(domain_parts) >= 2:
            return f"{domain_parts[-2]}.{domain_parts[-1]}"
        return parsed_url.netloc
    except (ValueError, AttributeError):
        return ""

def normalize_url(url: str) -> str:
    """Entfernt einen optionalen abschließenden Schrägstrich von einer URL."""
    if url.endswith('/'):
        return url[:-1]
    return url

def get_url_list_and_map(start_url: str, max_pages: int = None) -> tuple[list[str], dict[str, list[str]], list[str]]:
    """Durchsucht eine Website, um eine Liste interner URLs und eine Link-Map zu erstellen."""
    try:
        base_domain = get_base_domain(start_url)
        scheme = urlparse(start_url).scheme
        if not base_domain:
            return [], {}, []
    except (ValueError, AttributeError):
        return [], {}, []

    robots_url = f"{scheme}://{urlparse(start_url).netloc}/robots.txt"
    robot_parser = RobotFileParser()
    robot_parser.set_url(robots_url)
    try:
        robot_parser.read()
    except Exception as e:
        print(f"Konnte robots.txt nicht lesen: {e}")

    normalized_start_url = normalize_url(start_url)
    urls_to_visit = deque([normalized_start_url])
    visited_urls = {normalized_start_url}
    external_links = set()
    link_map = {}
    page_count = 0
    
    # KORREKTUR: Greift jetzt auf die Variable aus dem settings-Objekt zu
    crawl_limit = max_pages if max_pages is not None else settings.MAX_PAGES_TO_CRAWL

    while urls_to_visit and page_count < crawl_limit:
        current_url = urls_to_visit.popleft()

        if not robot_parser.can_fetch(settings.CRAWLER_USER_AGENT, current_url):
            continue

        page_count += 1
        link_map[current_url] = []

        if crawl_limit == 1 and page_count == 1:
            pass
        else:
            try:
                # KORREKTUR: Greift jetzt auf die Variablen aus dem settings-Objekt zu
                response = requests.get(
                    current_url, 
                    headers={'User-Agent': settings.CRAWLER_USER_AGENT}, 
                    timeout=settings.REQUEST_TIMEOUT
                )
                response.raise_for_status()

                if 'text/html' not in response.headers.get('Content-Type', ''):
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')

                for link_tag in soup.find_all('a', href=True):
                    href = link_tag['href']
                    absolute_url = urljoin(current_url, href)
                    
                    cleaned_url = urlparse(absolute_url)._replace(query="", fragment="").geturl()
                    normalized_cleaned_url = normalize_url(cleaned_url)

                    if not normalized_cleaned_url or urlparse(normalized_cleaned_url).scheme not in ['http', 'https']:
                        continue
                    
                    link_map[current_url].append(normalized_cleaned_url)

                    link_domain = get_base_domain(normalized_cleaned_url)
                    is_internal = link_domain == base_domain

                    if is_internal:
                        if normalized_cleaned_url not in visited_urls:
                            visited_urls.add(normalized_cleaned_url)
                            urls_to_visit.append(normalized_cleaned_url)
                    else:
                        external_links.add(normalized_cleaned_url)
            except Exception as e:
                print(f"Fehler beim Crawlen von {current_url}: {e}")

    return sorted(list(visited_urls)), link_map, sorted(list(external_links))