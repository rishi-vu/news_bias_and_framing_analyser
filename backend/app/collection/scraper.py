import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict

class ArticleScraper:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    def infer_source_name(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            
            # Map prominent domains
            domain_map = {
                "bbc.com": "BBC News",
                "bbc.co.uk": "BBC News",
                "cnn.com": "CNN",
                "foxnews.com": "Fox News",
                "reuters.com": "Reuters",
                "theguardian.com": "The Guardian",
                "nytimes.com": "The New York Times",
                "washingtonpost.com": "The Washington Post",
                "wsj.com": "The Wall Street Journal",
                "aljazeera.com": "Al Jazeera",
                "apnews.com": "Associated Press",
                "bloomberg.com": "Bloomberg",
                "politico.com": "Politico",
                "npr.org": "NPR",
                "ft.com": "Financial Times",
                "nbcnews.com": "NBC News",
            }
            for dom, name in domain_map.items():
                if dom in domain:
                    return name
            
            # Fallback to domain root capitalized
            base = domain.split(".")[0]
            return base.capitalize()
        except Exception:
            return "Unknown Source"

    def scrape_url(self, url: str, source_override: Optional[str] = None) -> Dict[str, str]:
        resp = requests.get(url, headers=self.headers, timeout=self.timeout)
        resp.raise_for_status()
        html = resp.text

        soup = BeautifulSoup(html, "html.parser")
        
        # Remove script, style, nav, footer, ads
        for elem in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "svg", "form"]):
            elem.decompose()

        # Extract title
        title = ""
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"].strip()
        elif soup.find("h1"):
            title = soup.find("h1").get_text(strip=True)
        elif soup.title:
            title = soup.title.get_text(strip=True)

        # Extract author
        author = ""
        meta_author = soup.find("meta", attrs={"name": "author"}) or soup.find("meta", property="article:author")
        if meta_author and meta_author.get("content"):
            author = meta_author["content"].strip()

        # Extract published date
        pub_date = ""
        meta_time = soup.find("meta", property="article:published_time") or soup.find("time")
        if meta_time:
            pub_date = meta_time.get("content") or meta_time.get_text(strip=True) or ""

        # Extract main text content
        paragraphs = []
        article_tag = soup.find("article") or soup.find("main") or soup.find(class_=re.compile(r"article|content|story|body", re.I))
        target_container = article_tag if article_tag else soup

        for p in target_container.find_all("p"):
            text = p.get_text(strip=True)
            # Filter out boilerplate, short navigation snippets
            if len(text.split()) >= 6:
                paragraphs.append(text)

        content = "\n\n".join(paragraphs)
        source = source_override or self.infer_source_name(url)

        return {
            "title": title or "Untitled Article",
            "content": content,
            "source": source,
            "url": url,
            "author": author,
            "published_date": pub_date,
        }

scraper = ArticleScraper()
