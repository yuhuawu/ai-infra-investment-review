# ai-infra-investment-review

A monthly AI infrastructure investment review tool for publicly traded stocks. It focuses on AI infrastructure, not application software, and turns a config-driven metric snapshot into layer scores, capex transmission estimates, rebalance proposals, and a Markdown report.

This repository is a v0.2 research scaffold. It can use mock data by default and limited live metadata adapters when explicitly requested. It does not connect to brokers or place trades.

## What It Does

- Reviews the AI infrastructure chain across L1-L6:
  - L1: semiconductor equipment, foundry, advanced packaging
  - L2: GPU, AI ASIC, accelerator silicon, interconnect
  - L3: HBM, DRAM, NAND, SSD, HDD
  - L4: networking, optics, servers, power, cooling
  - L5: cloud, LLM platform, AI compute providers
  - L6: cash, opportunity reserve, hedges
- Reads assumptions from `config/`.
- Uses mock metric snapshots by default; live mode fetches metadata, documents, and market metrics but does not do fragile one-off company filing parsers.
- Scores indicators, companies, and layers from `-2` to `+2`.
- Marks missing data as `missing` instead of inventing values.
- Marks model outputs as `model_estimated`.
- Confirms metrics through a catalog-driven validation framework before normal scoring.
- Populates market data metrics such as `price`, `market_cap`, `forward_pe`, `trailing_pe`, `ev_to_ebitda`, `price_to_sales`, `beta`, and `volatility` when the configured provider returns them.
- Blocks actionable rebalance proposals when confirmed metric coverage is below configured gates.
- Generates proposal-only rebalance suggestions.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python3 scripts/run_monthly_review.py --data-source mock
```

The script writes:

- `outputs/latest_report.md`
- `outputs/latest_scores.csv`
- `outputs/latest_metric_snapshot.json`
- `outputs/proposed_rebalance.csv`

### Mock vs Live

`--data-source mock` uses deterministic local mock data and is the default. It is the recommended mode for tests and repeatable development.

`--data-source live` uses real data-source adapters where available:

- SEC EDGAR filings metadata from `src/ai_infra_review/data_sources/sec.py`
- Investor relations document downloads from URLs in `config/data_sources.yaml`
- Market data from `src/ai_infra_review/data_sources/market.py`

Live mode is intentionally conservative. It downloads metadata/documents and can confirm provider-returned market metrics, but it does not perform fragile filing or press-release parsing. Any scoring metric that cannot be confirmed by a robust parser is emitted as `missing`.

You can pin the review date:

```bash
python3 scripts/run_monthly_review.py --data-source mock --as-of 2026-05-01
```

## Environment Variables

SEC live requests require:

```bash
export SEC_USER_AGENT="ai-infra-review your-email@example.com"
```

You can also copy `.env.example` to `.env` and edit the values:

```bash
cp .env.example .env
```

The runner loads `.env` automatically. `.env` is ignored by git.

Market data is optional. If no API key is present, the market adapter falls back to mock/missing market fields:

```bash
export MARKET_DATA_PROVIDER="fmp"          # supported: fmp, alphavantage, mock
export MARKET_DATA_API_KEY="..."
```

For `fmp`, the adapter uses quote, ratios/key-metrics, and profile-style endpoints where available. `forward_pe` is never fabricated from other multiples. If `forward_pe` is missing, `valuation_risk` may use `trailing_pe` or `price_to_sales` only when that fallback is explicitly allowed in `config/metric_catalog.yaml`.

Never commit API keys or personal tokens.

## Test

```bash
python3 -m pytest
```

If dependencies are not installed yet, install `requirements.txt` first. The runtime code itself can read the current JSON-subset YAML configs without PyYAML, but PyYAML remains the intended dependency for normal use.

## Data Provenance

Every metric uses one of these source types:

- `company_disclosed`
- `sec_xbrl`
- `market_data`
- `media_reported`
- `analyst_estimated`
- `model_estimated`
- `missing`

Each metric also has a status:

- `missing`
- `candidate`
- `validated`
- `confirmed`
- `conflict`

Reports and CSV outputs preserve these labels. Missing and unconfirmed values are not converted into zero-valued metrics. If a layer does not meet confirmed coverage gates, its score is set to `0` with `score_status=insufficient_data` and rebalance output becomes `no_action` when configured.

The canonical catalog lives at `config/metric_catalog.yaml`. It defines metric units, periods, accepted source types, range validators, scoring usage, and whether each metric is required for layer scoring.

## Data Quality Limits

- Live adapters are not complete parsers.
- SEC support currently fetches recent filings metadata by ticker/CIK.
- IR support downloads configured HTML/PDF/text documents but marks parsed metrics as `missing`.
- Market support returns `price`, `market_cap`, `forward_pe`, `trailing_pe`, `ev_to_ebitda`, `price_to_sales`, `beta`, and `volatility` when a configured provider supplies them; unavailable fields are `missing`.
- No test should access the real network; tests use mocked responses.

## Important Limits

This is research automation, not investment advice. Rebalance outputs are proposals for human review only. The project must not generate executable orders or connect to a brokerage API.
