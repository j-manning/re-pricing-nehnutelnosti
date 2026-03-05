# re-pricing-nehnutelnosti

Weekly scraper for **Nehnutelnosti.sk** listing fees (Slovakia).

## Platform

Nehnutelnosti.sk is Slovakia's leading real estate portal.

## Pricing Model

**Per-listing fee** with 4 package tiers:

| Tier | Fee (EUR) | Included features |
|------|-----------|------------------|
| Basic | €30 | Standard listing |
| Basic+ | €49 | Enhanced visibility |
| Optimum | €69 | Premium placement |
| Complete | €99 | Maximum exposure |

- `fee_period = per_listing`
- `currency = EUR`
- All prices include VAT

Source: [Nehnutelnosti.sk — Naše služby](https://www.nehnutelnosti.sk/nase-sluzby/inzercia/)

## Output

`data/pricing.csv` — 4 rows per scrape date, one per tier.

## Running Locally

```bash
pip install -r requirements.txt
python scraper.py
```
