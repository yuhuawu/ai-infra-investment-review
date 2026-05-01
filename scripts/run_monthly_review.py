#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_infra_review.capex_model import estimate_capex_transmission
from ai_infra_review.config import load_review_config
from ai_infra_review.data_sources.company_ir import fetch_investor_relations_updates
from ai_infra_review.data_sources.mock import load_mock_metric_snapshot
from ai_infra_review.data_sources.market import build_valuation_metric, fetch_market_snapshot
from ai_infra_review.data_sources.sec import SECConfigurationError, fetch_recent_filings
from ai_infra_review.metrics import metric_catalog_by_id, validate_metric_value
from ai_infra_review.rebalance import propose_rebalance
from ai_infra_review.report import build_monthly_report
from ai_infra_review.scoring import LayerScoreCalculator, flatten_score_rows, score_universe


def _write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the AI infrastructure monthly review.")
    parser.add_argument("--data-source", choices=["mock", "live"], default="mock")
    parser.add_argument("--as-of", help="Review date in YYYY-MM-DD format.")
    return parser.parse_args()


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _set_snapshot_as_of(snapshot: dict[str, Any], as_of: str | None) -> dict[str, Any]:
    if not as_of:
        return snapshot
    snapshot["as_of"] = as_of
    for company in snapshot.get("companies", []):
        for metric in company.get("metrics", {}).values():
            metric["as_of"] = as_of
            metric.setdefault("period", as_of)
    return snapshot


def _missing_metric(as_of: str | None, note: str = "Live adapter did not parse this metric.") -> dict[str, Any]:
    return {
        "value": None,
        "source_type": "missing",
        "status": "missing",
        "as_of": as_of,
        "period": as_of,
        "unit": None,
        "period_type": None,
        "evidence": [],
        "confidence": 0.0,
        "note": note,
    }


def _canonicalize_metric_snapshot(snapshot: dict[str, Any], metric_catalog: dict[str, Any]) -> dict[str, Any]:
    specs = metric_catalog_by_id(metric_catalog)
    for company in snapshot.get("companies", []):
        metrics = company.get("metrics", {})
        for metric_id, raw_metric in list(metrics.items()):
            metrics[metric_id] = validate_metric_value(metric_id, raw_metric, specs.get(metric_id))
    return snapshot


def _set_market_metric_as_of(metric: dict[str, Any], as_of: str | None) -> dict[str, Any]:
    if not as_of:
        return metric
    metric["as_of"] = as_of
    metric["period"] = as_of
    return metric


def _build_live_metric_snapshot(config, as_of: str | None) -> dict[str, Any]:
    holdings = config.portfolio["holdings"]
    tickers = [holding["ticker"] for holding in holdings if holding["ticker"] != "CASH"]
    companies = []
    for holding in holdings:
        layer = holding["layer"]
        layer_indicators = config.indicators.get("layers", {}).get(layer, {})
        companies.append(
            {
                "ticker": holding["ticker"],
                "layer": layer,
                "metrics": {
                    indicator: _missing_metric(as_of, "Live data downloaded as metadata only; robust metric parser not implemented.")
                    for indicator in layer_indicators
                },
            }
        )

    sec_filings = {
        ticker: fetch_recent_filings(ticker=ticker, limit=5)
        for ticker in tickers
    }
    ir_updates = {
        ticker: fetch_investor_relations_updates(ticker, config.data_sources)
        for ticker in tickers
    }
    market_snapshot = fetch_market_snapshot(tickers)
    specs = metric_catalog_by_id(config.metric_catalog)
    companies_by_ticker = {company["ticker"]: company for company in companies}
    for ticker, market_row in market_snapshot.items():
        company = companies_by_ticker.get(ticker)
        if not company:
            continue
        metrics = company.setdefault("metrics", {})
        for metric_id, raw_metric in market_row.items():
            if metric_id in {"ticker", "provider"}:
                continue
            metrics[metric_id] = validate_metric_value(
                metric_id,
                _set_market_metric_as_of(dict(raw_metric), as_of),
                specs.get(metric_id),
            )
        if "valuation_risk" in metrics:
            metrics["valuation_risk"] = build_valuation_metric(ticker, market_row, config.metric_catalog, as_of=as_of)

    return {
        "as_of": as_of,
        "data_source": "live",
        "companies": companies,
        "live_metadata": {
            "sec_filings": sec_filings,
            "company_ir": ir_updates,
            "market": market_snapshot,
        },
    }


def _load_metric_snapshot(config, *, data_source: str, as_of: str | None) -> dict[str, Any]:
    if data_source == "mock":
        return _set_snapshot_as_of(load_mock_metric_snapshot(), as_of)
    return _build_live_metric_snapshot(config, as_of)


def main() -> None:
    args = _parse_args()
    _load_dotenv(ROOT / ".env")
    config = load_review_config(ROOT / "config")
    try:
        metric_snapshot = _load_metric_snapshot(config, data_source=args.data_source, as_of=args.as_of)
        metric_snapshot = _canonicalize_metric_snapshot(metric_snapshot, config.metric_catalog)
    except SECConfigurationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    company_scores = score_universe(metric_snapshot, config.indicators, config.metric_catalog)
    layer_scores = LayerScoreCalculator(
        config.indicators,
        config.layers,
        config.metric_catalog,
        config.portfolio["constraints"],
    ).calculate(metric_snapshot)
    capex_results = estimate_capex_transmission(config.capex_transmission)
    rebalance = propose_rebalance(
        holdings=config.portfolio["holdings"],
        layers=config.portfolio.get("layer_targets", config.layers),
        layer_scores=layer_scores,
        company_scores=company_scores,
        constraints=config.portfolio["constraints"],
    )
    report = build_monthly_report(
        config=config,
        metric_snapshot=metric_snapshot,
        company_scores=company_scores,
        layer_scores=layer_scores,
        capex_results=capex_results,
        rebalance=rebalance,
    )

    output_dir = ROOT / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "latest_report.md").write_text(report, encoding="utf-8")
    output_snapshot = {
        **metric_snapshot,
        "capex_transmission": capex_results,
    }
    (output_dir / "latest_metric_snapshot.json").write_text(
        json.dumps(output_snapshot, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    _write_csv(
        output_dir / "latest_scores.csv",
        flatten_score_rows(company_scores, layer_scores),
        [
            "scope",
            "layer",
            "ticker",
            "indicator",
            "label",
            "value",
            "source_type",
            "status",
            "score_status",
            "confirmed_metric_coverage",
            "score",
            "total_score",
            "demand_score",
            "supply_bottleneck_score",
            "margin_score",
            "valuation_score",
            "order_visibility_score",
            "weight",
            "weighted_score",
            "reason",
            "confidence",
            "note",
        ],
    )
    _write_csv(
        output_dir / "proposed_rebalance.csv",
        rebalance,
        [
            "ticker",
            "layer",
            "action",
            "current_weight",
            "proposed_weight",
            "delta_weight",
            "reason",
            "confidence",
            "constraint_flags",
        ],
    )
    print(f"Wrote monthly review outputs to {output_dir}")


if __name__ == "__main__":
    main()
