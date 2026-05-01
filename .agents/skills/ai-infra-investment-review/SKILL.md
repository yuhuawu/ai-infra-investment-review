---
name: ai-infra-investment-review
description: Run this repo's monthly AI infrastructure investment review workflow. Use for monthly AI infrastructure investment review, AI capex transmission analysis, hyperscaler capex update impact analysis, and AI semiconductor, cloud, and datacenter portfolio review using the repository's configs, mock data, scripts, and outputs.
---

# AI Infrastructure Investment Review

Use this skill from the repository root. The workflow is offline-only unless the user explicitly asks to change the project design.

## Core Workflow

1. Read the review configuration:
   - `config/layers.yaml`
   - `config/indicators.yaml`
   - `config/portfolio.yaml`
   - `config/capex_transmission.yaml`
2. Use the repository implementation under `src/ai_infra_review/`.
3. Run the monthly review:

```bash
.venv/bin/python scripts/run_monthly_review.py
```

If `.venv/bin/python` is unavailable, use `python3 scripts/run_monthly_review.py`.

4. Inspect:
   - `outputs/latest_report.md`
   - `outputs/latest_scores.csv`
   - `outputs/latest_metric_snapshot.json`
   - `outputs/proposed_rebalance.csv`
5. Summarize the important findings for the user in the default output format below.

## References

Read these when methodology, data provenance, or output interpretation matters:

- `references/framework.md`
- `references/data_sources.md`

## Safety Rules

- Never execute trades.
- Never connect to brokerage APIs.
- Never fabricate missing data.
- Label all estimates clearly, especially `model_estimated` outputs.
- Cite or record data sources where available.
- Ask for human confirmation before changing `config/portfolio.yaml`.
- Treat rebalance output as a proposal only, not an order instruction.

## Default Output Format

When reporting results to the user, use this structure:

1. Layer score summary
2. Top positive changes
3. Top negative changes
4. Capex transmission events
5. Proposed rebalance
6. Data gaps
7. Recommended next checks

Keep the summary concise, but include enough detail for a human to decide what to inspect next.
