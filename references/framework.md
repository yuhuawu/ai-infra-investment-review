# AI Infrastructure Investment Review Framework

This project implements the v0.1 offline version of the framework in `references/plan.md`.

The core question is not "is AI hot?" The monthly review asks:

- Who is spending capex?
- Who is receiving orders?
- Which bottleneck is tightening?
- Who is preserving margin and cash flow?
- Has valuation already priced in the improvement?

## Layer Model

The review covers public-market AI infrastructure exposure across six layers:

| Layer | Focus |
| --- | --- |
| L1 | Semiconductor equipment, foundry, advanced packaging |
| L2 | GPU, AI ASIC, accelerator silicon, interconnect |
| L3 | HBM, DRAM, NAND, SSD, HDD |
| L4 | Networking, optics, servers, power, cooling |
| L5 | Cloud, LLM platform, AI compute providers |
| L6 | Cash, opportunity reserve, hedges |

Application software is out of scope unless it directly affects cloud infrastructure demand.

## Monthly Scoring

Each layer is scored from `-2` to `+2` using five broad dimensions:

- Demand: hyperscaler capex, cloud revenue, RPO/backlog, AI usage.
- Bottlenecks: HBM, advanced packaging, power, cooling, networking, supply tightness.
- Margin: whether revenue growth is becoming profit rather than only capex.
- Valuation: whether EPS revisions support the move.
- Order visibility: backlog, book-to-bill, RPO, and guidance.

Company and layer scores are weighted aggregates of configured indicators. Missing metrics score `0` but stay visible as missing.

## Data Provenance

Every metric must use exactly one source type:

- `company_disclosed`
- `media_reported`
- `analyst_estimated`
- `model_estimated`
- `missing`

Do not fabricate values. If a value is not available, set `value: null` and `source_type: missing`.

## Capex Transmission

The capex model converts a hyperscaler capex increment into vendor-level scenario estimates:

```text
incremental_revenue =
  capex_increment
  * category_share
  * vendor_share
  * revenue_capture
  * timing_factor

incremental_operating_income =
  incremental_revenue * margin

incremental_net_income =
  incremental_operating_income * (1 - tax_rate)

implied_market_cap_impact =
  incremental_net_income * forward_pe

implied_market_cap_impact_pct =
  implied_market_cap_impact / market_cap
```

All outputs from this model are `model_estimated`.

## Rebalance Discipline

Rebalance proposals are human-review suggestions only:

- Add layers whose scores improve, subject to max weights.
- Trim layers with weak scores, especially cyclical or highly valued areas.
- Maintain a cash/opportunity reserve.
- Watch missing-data-heavy or high-risk names.
- Never produce executable trade instructions.
