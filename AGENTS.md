# AI Infra Investment Review Agents

Codex work in this repository must preserve the v0.1 offline research contract.

## Required Workflow

- Read `references/plan.md` and `references/framework.md` before changing review methodology.
- Keep assumptions in `config/` whenever practical.
- Run tests after changing scoring, capex transmission, rebalance, or report output:

```bash
python3 -m pytest
```

- Run the sample review after changing output behavior:

```bash
python3 scripts/run_monthly_review.py
```

## Hard Prohibitions

- Do not connect to broker APIs.
- Do not generate automatic orders.
- Do not scrape webpages or call real market/filing/company APIs in v0.1.
- Do not fabricate missing data.
- Do not present outputs as investment advice.

## Data Rules

- Missing data must be represented as `source_type: missing` and `value: null`.
- Model-derived values must be represented as `source_type: model_estimated`.
- Reports must distinguish:
  - `company_disclosed`
  - `media_reported`
  - `analyst_estimated`
  - `model_estimated`
  - `missing`
- Scores must stay in the `-2` to `+2` range.

## Output Contract

The monthly review script must generate:

- `outputs/latest_report.md`
- `outputs/latest_scores.csv`
- `outputs/latest_metric_snapshot.json`
- `outputs/proposed_rebalance.csv`
