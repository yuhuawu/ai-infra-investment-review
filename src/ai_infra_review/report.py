from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Any

from .config import ReviewConfig
from .metrics import SOURCE_TYPES
from .scoring import rank_company_scores


def _source_counts(metric_snapshot: dict[str, Any], capex_results: dict[str, Any]) -> Counter:
    counts: Counter = Counter()
    for company in metric_snapshot.get("companies", []):
        for metric in company.get("metrics", {}).values():
            counts[metric.get("source_type", "missing")] += 1
    for scenario in capex_results.get("scenarios", {}).values():
        for impact in scenario.get("ticker_impacts", []):
            counts[impact["source_type"]] += 1
        counts[scenario["buyer_impact"]["source_type"]] += 1
    return counts


def _missing_metrics(metric_snapshot: dict[str, Any]) -> list[str]:
    missing = []
    for company in metric_snapshot.get("companies", []):
        for name, metric in company.get("metrics", {}).items():
            if metric.get("status") in {"missing", "candidate", "conflict"} or metric.get("source_type") == "missing" or metric.get("value") is None:
                missing.append(f"{company['ticker']} / {name}: {metric.get('note', 'missing')}")
    return missing


def _metric_status_counts(metric_snapshot: dict[str, Any]) -> Counter:
    counts: Counter = Counter()
    for company in metric_snapshot.get("companies", []):
        for metric in company.get("metrics", {}).values():
            counts[metric.get("status", "missing")] += 1
    return counts


def _valuation_coverage(metric_snapshot: dict[str, Any]) -> dict[str, Any]:
    rows = []
    counts: Counter = Counter()
    for company in metric_snapshot.get("companies", []):
        metric = company.get("metrics", {}).get("valuation_risk", {})
        status = metric.get("status", "missing")
        source_metric = metric.get("metadata", {}).get("valuation_source_metric", "none")
        counts[(status, source_metric)] += 1
        rows.append(
            {
                "ticker": company.get("ticker"),
                "status": status,
                "source_metric": source_metric,
                "value": metric.get("value"),
            }
        )
    confirmed = sum(1 for row in rows if row["status"] == "confirmed")
    return {
        "rows": rows,
        "confirmed": confirmed,
        "total": len(rows),
        "counts": counts,
    }


def _major_changes(layer_scores: list[dict[str, Any]], rebalance: list[dict[str, Any]]) -> list[str]:
    strongest = max(layer_scores, key=lambda row: row.get("total_score", row.get("score", 0.0)))
    weakest = min(layer_scores, key=lambda row: row.get("total_score", row.get("score", 0.0)))
    largest_delta = max(rebalance, key=lambda row: abs(float(row["delta_weight"])))
    return [
        f"Strongest layer is {strongest['layer']} at {strongest['total_score']:.2f}.",
        f"Weakest layer is {weakest['layer']} at {weakest['total_score']:.2f}.",
        f"Largest proposal delta is {largest_delta['ticker']} at {largest_delta['delta_weight']:.2%}.",
    ]


def build_monthly_report(
    config: ReviewConfig,
    metric_snapshot: dict[str, Any],
    company_scores: list[dict[str, Any]],
    layer_scores: list[dict[str, Any]],
    capex_results: dict[str, Any],
    rebalance: list[dict[str, Any]],
) -> str:
    ranked_companies = rank_company_scores(company_scores)
    source_counts = _source_counts(metric_snapshot, capex_results)
    status_counts = _metric_status_counts(metric_snapshot)
    valuation_coverage = _valuation_coverage(metric_snapshot)
    missing_metrics = _missing_metrics(metric_snapshot)
    capex_event = capex_results["event"]
    base_scenario = capex_results["scenarios"]["base"]
    buyer = base_scenario["buyer_impact"]
    top_vendor_impacts = base_scenario["ticker_impacts"][:8]

    data_source = metric_snapshot.get("data_source", "mock")
    source_sentence = (
        "This report is a research workflow output, not investment advice. "
        f"It was generated in `{data_source}` data-source mode."
    )
    lines = [
        f"# AI Infrastructure Monthly Review - {date.today().isoformat()}",
        "",
        source_sentence,
        "",
        "## Executive summary",
        "",
        f"- Review universe covers {len(company_scores)} public-equity or cash-reserve entries across L1-L6.",
        "- Layer scores include demand, supply bottleneck, margin, valuation, and order visibility dimensions.",
        f"- Capex scenario set includes: {', '.join(capex_results['scenarios'].keys())}.",
        "",
        "## Layer score table",
        "",
        "| Layer | Name | Status | Coverage | Demand | Supply | Margin | Valuation | Orders | Total | Reason |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for layer in layer_scores:
        lines.append(
            "| {layer} | {layer_name} | {score_status} | {confirmed_metric_coverage:.0%} | {demand_score:.2f} | {supply_bottleneck_score:.2f} | {margin_score:.2f} | {valuation_score:.2f} | {order_visibility_score:.2f} | {total_score:.2f} | {reason} |".format(
                **layer
            )
        )

    lines.extend(["", "## Major changes", ""])
    lines.extend(f"- {item}" for item in _major_changes(layer_scores, rebalance))

    lines.extend(
        [
            "",
            "## Company observations",
            "",
            "| Ticker | Layer | Score | Missing metrics | Observation |",
            "| --- | --- | ---: | ---: | --- |",
        ]
    )
    for company in ranked_companies:
        observation = "missing data needs review" if company["missing_count"] else "complete mock metric set"
        lines.append(
            "| {ticker} | {layer} | {score:.2f} | {missing_count} | {observation} |".format(
                observation=observation,
                **company,
            )
        )

    lines.extend(
        [
            "",
            "## Capex transmission events",
            "",
            f"Event source type: `{capex_event.get('source_type')}`. All calculated impacts below are `model_estimated`.",
            "",
            "| Scenario | Ticker | Categories | Incremental revenue | EBIT impact | Net income impact | Market cap impact | Stock impact | Confidence |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for scenario_name, scenario in capex_results["scenarios"].items():
        for impact in scenario["ticker_impacts"][:5]:
            lines.append(
                "| {scenario} | {ticker} | {categories} | ${incremental_revenue:,.0f} | ${incremental_ebit:,.0f} | ${incremental_net_income:,.0f} | ${estimated_market_cap_impact:,.0f} | {estimated_stock_impact_pct:.2%} | {confidence:.2f} |".format(
                    **{**impact, "scenario": scenario_name},
                )
            )
    lines.extend(
        [
            "",
            f"Base-case buyer FCF pressure: ${buyer['fcf_pressure']:,.0f}.",
            "",
            "## Proposed rebalance",
            "",
            "| Ticker | Action | Current | Proposed | Delta | Confidence | Constraint flags | Reason |",
            "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for row in rebalance:
        lines.append(
            "| {ticker} | {action} | {current_weight:.2%} | {proposed_weight:.2%} | {delta_weight:.2%} | {confidence:.2f} | {constraint_flags} | {reason} |".format(
                **row
            )
        )

    lines.extend(
        [
            "",
            "## Data Quality",
            "",
            "| Layer | Score status | Confirmed metric coverage | Required metrics | Confirmed metrics |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    for layer in layer_scores:
        lines.append(
            "| {layer} | {score_status} | {confirmed_metric_coverage:.0%} | {required_metric_count} | {confirmed_metric_count} |".format(
                **layer
            )
        )
    lines.extend(["", "Metric status counts:"])
    for status in ["confirmed", "validated", "candidate", "conflict", "missing"]:
        lines.append(f"- `{status}`: {status_counts.get(status, 0)}")

    lines.extend(
        [
            "",
            "Valuation data coverage:",
            f"- confirmed valuation metrics: {valuation_coverage['confirmed']} / {valuation_coverage['total']}",
        ]
    )
    for (status, source_metric), count in sorted(valuation_coverage["counts"].items()):
        lines.append(f"- `{status}` via `{source_metric}`: {count}")

    lines.extend(["", "## Risks and missing data", ""])
    if missing_metrics:
        lines.extend(f"- {item}" for item in missing_metrics)
    else:
        lines.append("- None")
    lines.extend(
        [
            "- Rebalance output is a proposal only; no order quantity or broker instruction is generated.",
            "- Capex transmission estimates are scenario model outputs, not forecasts.",
            "",
            "## Data quality notes",
            "",
        ]
    )
    for source_type in sorted(SOURCE_TYPES):
        lines.append(f"- `{source_type}`: {source_counts.get(source_type, 0)}")
    lines.extend(
        [
            "- Missing data remains `missing`; it is not fabricated or backfilled.",
            "- All model outputs are labeled `model_estimated`.",
            "",
        ]
    )
    return "\n".join(lines)
