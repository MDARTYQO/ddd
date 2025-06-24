import requests
from bs4 import BeautifulSoup
import json
import sys

def duckduckgo_search(query):
    url = f"https://html.duckduckgo.com/html/?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for a in soup.find_all('a', class_='result__a'):
        results.append({
            "title": a.text,
            "link": a['href']
        })
    return results

if __name__ == "__main__":
    query = sys.argv[1]
    results = duckduckgo_search(query)
    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
