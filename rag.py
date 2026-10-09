import os
import re
import requests
import wikipediaapi

wiki = wikipediaapi.Wikipedia(user_agent="ArgueWithHistory/1.0", language="en")


def slug(name):
    s = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")[:50]
    return s if len(s) >= 3 else s + "_fig"


def search_wiki(query):
    r = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={"action": "query", "list": "search", "srsearch": query,
                "srlimit": 5, "format": "json"},
        headers={"User-Agent": "ArgueWithHistory/1.0"},
        timeout=10,
    )
    return [x["title"] for x in r.json()["query"]["search"]]


def fetch_wiki(title, key):
    page = wiki.page(title)
    if not page.exists():
        return None
    folder = f"data/{key}"
    os.makedirs(folder, exist_ok=True)
    with open(f"{folder}/wiki.txt", "w", encoding="utf-8") as f:
        f.write(page.text)
    return page


def _chunks(key):
    folder = f"data/{key}"
    out = []
    if not os.path.isdir(folder):
        return out
    for fname in os.listdir(folder):
        if not fname.endswith(".txt"):
            continue
        with open(f"{folder}/{fname}", encoding="utf-8") as f:
            text = f.read()
        for i in range(0, len(text), 700):
            out.append(text[i:i + 800])
    return out


def load_figure(key, wiki_title=None):
    if _chunks(key):
        return True
    if wiki_title and fetch_wiki(wiki_title, key):
        return bool(_chunks(key))
    return False


def retrieve(key, query, n=4):
    chunks = _chunks(key)
    if not chunks:
        return ""
    words = set(re.findall(r"[a-z0-9]{3,}", query.lower()))
    scored = []
    for i, c in enumerate(chunks):
        cw = set(re.findall(r"[a-z0-9]{3,}", c.lower()))
        scored.append((len(words & cw), -i, c))
    scored.sort(reverse=True)
    return "\n---\n".join(c for _, _, c in scored[:n])