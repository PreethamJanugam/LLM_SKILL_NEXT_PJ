import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from urllib.parse import urljoin 
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

def fetch_website_contents(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() 
        soup = BeautifulSoup(response.content, "html.parser")
        
        title = soup.title.string if soup.title else "No title found"
        
        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            text = soup.body.get_text(separator="\n", strip=True)
        else:
            text = ""
            
        return (title + "\n\n" + text)[:2_000]
        
    except RequestException as e:
        # Crucial: Return a string, do not let the error bubble up and crash the notebook
        return f"Error fetching {url}: {str(e)}"
def fetch_website_links(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        # 1. Safely extract hrefs
        raw_links = [link.get("href") for link in soup.find_all("a") if link.get("href")]
        
        # 2. Filter out non-web links and deterministically join relative links
        clean_links = []
        for link in raw_links:
            if not link.startswith(('mailto:', 'tel:', 'javascript:')):
                # urljoin intelligently combines "thttps://gihub.com" and "/newsroom"
                # into "https://github.com/newsroom"
                absolute_url = urljoin(url, link) 
                clean_links.append(absolute_url)
        
        # 3. Remove duplicates by converting to a set, then back to a list
        return list(set(clean_links))
        
    except RequestException as e:
        print(f"Warning: Could not fetch links from {url}. Error: {e}")
        return []