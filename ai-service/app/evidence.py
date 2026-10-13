import requests
from urllib.parse import quote
import xml.etree.ElementTree as ET
import re


MAX_EVIDENCE = 5


STOP_WORDS = {
    "the", "and", "for", "are", "was", "were",
    "this", "that", "with", "from", "will",
    "have", "has", "had", "been", "they",
    "their", "about", "said", "today", "into",
    "after", "before", "which", "when", "what",
    "who", "how", "why", "its", "can", "could",
    "government", "announced", "policy"
}


def get_keywords(text):
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())

    return {
        word for word in words
        if word not in STOP_WORDS
    }


def relevance_score(claim, title):
    claim_keywords = get_keywords(claim)
    title_keywords = get_keywords(title)

    if not claim_keywords or not title_keywords:
        return 0.0

    common_words = claim_keywords.intersection(title_keywords)

    return len(common_words) / len(claim_keywords)


def get_country(text):
    text = text.lower()

    if re.search(r"\b(canada|canadian|first nations)\b", text):
        return "canada"

    if re.search(r"\b(india|indian|modi|new delhi)\b", text):
        return "india"

    return None


def fetch_rss(query):
    url = (
        "https://news.google.com/rss/search?q="
        + quote(query)
        + "&hl=en-IN&gl=IN&ceid=IN:en"
    )

    try:
        response = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        response.raise_for_status()
        root = ET.fromstring(response.content)

        results = []

        for item in root.findall(".//item"):
            title = item.findtext("title") or ""
            link = item.findtext("link") or ""

            source_element = item.find("source")

            if source_element is not None:
                source = source_element.text or "Unknown"
            else:
                source = "Unknown"

            if title and link:
                results.append({
                    "title": title,
                    "source": source,
                    "url": link
                })

        return results

    except (
        requests.RequestException,
        ET.ParseError,
        ValueError
    ):
        return []


def fetch_reference_sources(claim):
    """Search Wikipedia for reference pages related to a claim."""
    url = "https://en.wikipedia.org/w/rest.php/v1/search/page"

    try:
        response = requests.get(
            url,
            params={
                "q": claim,
                "limit": MAX_EVIDENCE
            },
            headers={
                "User-Agent": "FakeNewsDNAAnalyzer/1.0"
            },
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        results = []

        for page in data.get("pages", []):
            title = page.get("title", "")

            if not title:
                continue

            results.append({
                "title": title,
                "source": "Wikipedia",
                "url": (
                    "https://en.wikipedia.org/wiki/"
                    + quote(title.replace(" ", "_"))
                ),
                "description": page.get("description", ""),
                "excerpt": page.get("excerpt", "")
            })

        return results

    except (requests.RequestException, ValueError):
        return []


def search_evidence(claim):
    results = fetch_rss(claim)

    claim_country = get_country(claim)
    unique_results = {}

    for item in results:
        title = item.get("title", "")
        url = item.get("url", "")

        if not title or not url:
            continue

        title_country = get_country(title)

        # Reject clearly mismatched countries
        if (
            claim_country is not None
            and title_country is not None
            and claim_country != title_country
        ):
            continue

        score = relevance_score(claim, title)

        # Filter weak keyword matches
        if score < 0.30:
            continue

        item["relevance_score"] = round(score, 2)

        if url not in unique_results:
            unique_results[url] = item

    filtered_results = list(unique_results.values())

    filtered_results.sort(
        key=lambda item: item["relevance_score"],
        reverse=True
    )

    return filtered_results[:MAX_EVIDENCE]


def verify_evidence(claim, evidence):
    if not evidence:
        return {
            "claim": claim,
            "status": "UNVERIFIED",
            "evidence_count": 0,
            "match_score": 0,
            "message": (
                "No relevant evidence found. "
                "The claim could not be verified."
            )
        }

    best_score = max(
        item.get("relevance_score", 0)
        for item in evidence
    )

    return {
        "claim": claim,
        "status": "RELEVANT EVIDENCE FOUND - MANUAL VERIFICATION NEEDED",
        "evidence_count": len(evidence),
        "match_score": round(best_score, 2),
        "message": (
            "Related sources were found. "
            "Their headlines alone cannot establish "
            "whether the claim is true or false."
        )
    }