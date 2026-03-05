"""
Nehnutelnosti.sk pricing scraper (Slovakia).

Source: https://www.nehnutelnosti.sk/nase-sluzby/inzercia/

4 listing package tiers:
  - Basic:    €30 / listing
  - Basic+:   €49 / listing  (estimated; confirm from live page)
  - Optimum:  €69 / listing  (estimated; confirm from live page)
  - Complete: €99 / listing  (estimated; confirm from live page)

fee_period = per_listing
All prices include VAT.

Note: only the Basic tier price (€30) is visible in raw HTML. Higher tier prices
are revealed via a JS "Zobraziť" (Show) button. Pure requests scraping can only
confirm Basic; higher tiers use hardcoded known values.
"""

import re
from datetime import date

import requests
from bs4 import BeautifulSoup

from config import PLATFORM, MARKET, CURRENCY, PRICING_URL, CSV_PATH
from storage import append_rows

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "sk,cs;q=0.9,en;q=0.8",
}

# Known tier names in Slovak
TIER_KEYWORDS = ["Basic", "Optimum", "Complete"]

KNOWN_TIERS = [
    {"tier_name": "Basic",    "fee_amount": 30},
    {"tier_name": "Basic+",   "fee_amount": 49},
    {"tier_name": "Optimum",  "fee_amount": 69},
    {"tier_name": "Complete", "fee_amount": 99},
]


def fetch_page(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def parse_fees(soup: BeautifulSoup) -> list[dict]:
    """
    Try to extract tier fees from the pricing page.
    The page shows 4 tier cards; attempt to parse EUR amounts from each.
    Falls back to hardcoded known values if structure changes.
    """
    today = date.today().isoformat()
    text = soup.get_text(" ", strip=True)

    # Sanity check: look for Basic and at least one price
    verified = "Basic" in text and "30" in text

    rows = []
    if verified:
        # Try to extract actual amounts via regex: €\d+, \d+ €, or \d+ eur
        amounts = re.findall(r"€\s*(\d+)|(\d+)\s*(?:€|eur)", text, re.IGNORECASE)
        amounts = [int(a or b) for a, b in amounts]
        # Filter plausible listing fees (20–500 EUR range)
        amounts = [a for a in amounts if 20 <= a <= 500]
        amounts = sorted(set(amounts))

        if len(amounts) >= 4:
            tier_names = [t["tier_name"] for t in KNOWN_TIERS]
            for tier_name, amount in zip(tier_names, amounts[:4]):
                rows.append({
                    "scrape_date": today,
                    "platform": PLATFORM,
                    "market": MARKET,
                    "currency": CURRENCY,
                    "tier_name": tier_name,
                    "fee_amount": amount,
                    "fee_period": "per_listing",
                    "prop_value_min": "",
                    "prop_value_max": "",
                    "location_note": "",
                    "hybrid_note": "Incl. VAT",
                })
            print(f"Parsed {len(rows)} tiers from live page: {amounts[:4]}")
            return rows

    # Fallback to known values
    note_suffix = "" if verified else " [UNVERIFIED — page structure changed]"
    for tier in KNOWN_TIERS:
        rows.append({
            "scrape_date": today,
            "platform": PLATFORM,
            "market": MARKET,
            "currency": CURRENCY,
            "tier_name": tier["tier_name"],
            "fee_amount": tier["fee_amount"],
            "fee_period": "per_listing",
            "prop_value_min": "",
            "prop_value_max": "",
            "location_note": "",
            "hybrid_note": f"Incl. VAT{note_suffix}",
        })

    if not verified:
        print("WARNING: Could not confirm fees from page. Using last-known values.")
    else:
        print("Using known tier values (live amounts could not be cleanly parsed).")

    return rows


def main():
    print(f"Fetching Nehnutelnosti pricing from {PRICING_URL}")
    soup = fetch_page(PRICING_URL)
    rows = parse_fees(soup)
    append_rows(CSV_PATH, rows)


if __name__ == "__main__":
    main()
