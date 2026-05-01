from __future__ import annotations

from typing import Any

from .metrics import SOURCE_MODEL_ESTIMATED

SCENARIO_ORDER = ("conservative", "base", "aggressive")


def _default_scenarios() -> dict[str, dict[str, float]]:
    return {
        "conservative": {
            "capex_multiplier": 0.70,
            "revenue_capture_multiplier": 0.85,
            "margin_multiplier": 0.90,
            "confidence": 0.55,
        },
        "base": {
            "capex_multiplier": 1.00,
            "revenue_capture_multiplier": 1.00,
            "margin_multiplier": 1.00,
            "confidence": 0.70,
        },
        "aggressive": {
            "capex_multiplier": 1.30,
            "revenue_capture_multiplier": 1.10,
            "margin_multiplier": 1.05,
            "confidence": 0.50,
        },
    }


def estimate_vendor_impact(
    *,
    hyperscaler: str,
    capex_increment: float,
    category: str,
    category_share: float,
    vendor: dict[str, Any],
    scenario: str = "base",
    scenario_assumptions: dict[str, float] | None = None,
) -> dict[str, Any]:
    assumptions = scenario_assumptions or _default_scenarios()["base"]
    scenario_capex = capex_increment * float(assumptions.get("capex_multiplier", 1.0))
    revenue_capture = float(vendor["revenue_capture"]) * float(assumptions.get("revenue_capture_multiplier", 1.0))
    margin = float(vendor["margin"]) * float(assumptions.get("margin_multiplier", 1.0))
    category_capex = scenario_capex * category_share
    incremental_revenue = (
        scenario_capex
        * category_share
        * float(vendor["vendor_share"])
        * revenue_capture
        * float(vendor.get("timing_factor", 1.0))
    )
    incremental_ebit = incremental_revenue * margin
    incremental_net_income = incremental_ebit * (1.0 - float(vendor["tax_rate"]))
    estimated_market_cap_impact = incremental_net_income * float(vendor["forward_pe"])
    market_cap = float(vendor["market_cap"])

    return {
        "scenario": scenario,
        "hyperscaler": hyperscaler,
        "ticker": vendor["ticker"],
        "layer": vendor["layer"],
        "category": category,
        "category_capex": round(category_capex, 2),
        "category_share": category_share,
        "vendor_share": float(vendor["vendor_share"]),
        "revenue_capture": round(revenue_capture, 6),
        "timing_factor": float(vendor.get("timing_factor", 1.0)),
        "incremental_revenue": round(incremental_revenue, 2),
        "incremental_ebit": round(incremental_ebit, 2),
        "incremental_net_income": round(incremental_net_income, 2),
        "forward_pe": float(vendor["forward_pe"]),
        "market_cap": market_cap,
        "estimated_market_cap_impact": round(estimated_market_cap_impact, 2),
        "estimated_stock_impact_pct": round(estimated_market_cap_impact / market_cap, 6) if market_cap else 0.0,
        "assumptions_used": {
            "capex_increment": capex_increment,
            "scenario_capex_increment": scenario_capex,
            "category_share": category_share,
            "vendor_share": float(vendor["vendor_share"]),
            "revenue_capture": round(revenue_capture, 6),
            "margin": round(margin, 6),
            "tax_rate": float(vendor["tax_rate"]),
            "forward_pe": float(vendor["forward_pe"]),
            "market_cap": market_cap,
        },
        "confidence": float(assumptions.get("confidence", 0.6)),
        "source_type": SOURCE_MODEL_ESTIMATED,
        "note": "Scenario output from capex transmission model.",
    }


def _aggregate_ticker_impacts(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    aggregated: dict[str, dict[str, Any]] = {}
    for row in rows:
        ticker = row["ticker"]
        if ticker not in aggregated:
            aggregated[ticker] = {
                "scenario": row["scenario"],
                "hyperscaler": row["hyperscaler"],
                "ticker": ticker,
                "layer": row["layer"],
                "categories": [],
                "incremental_revenue": 0.0,
                "incremental_ebit": 0.0,
                "incremental_net_income": 0.0,
                "estimated_market_cap_impact": 0.0,
                "market_cap": row["market_cap"],
                "assumptions_used": [],
                "confidence": row["confidence"],
                "source_type": SOURCE_MODEL_ESTIMATED,
            }
        target = aggregated[ticker]
        target["categories"].append(row["category"])
        target["incremental_revenue"] += row["incremental_revenue"]
        target["incremental_ebit"] += row["incremental_ebit"]
        target["incremental_net_income"] += row["incremental_net_income"]
        target["estimated_market_cap_impact"] += row["estimated_market_cap_impact"]
        target["assumptions_used"].append(row["assumptions_used"])
        target["confidence"] = round(min(target["confidence"], row["confidence"]), 4)

    outputs = []
    for row in aggregated.values():
        market_cap = float(row["market_cap"])
        row["categories"] = ",".join(row["categories"])
        row["incremental_revenue"] = round(row["incremental_revenue"], 2)
        row["incremental_ebit"] = round(row["incremental_ebit"], 2)
        row["incremental_net_income"] = round(row["incremental_net_income"], 2)
        row["estimated_market_cap_impact"] = round(row["estimated_market_cap_impact"], 2)
        row["estimated_stock_impact_pct"] = round(row["estimated_market_cap_impact"] / market_cap, 6) if market_cap else 0.0
        row["note"] = "Aggregated ticker impact across capex categories."
        outputs.append(row)
    return sorted(outputs, key=lambda item: (-item["estimated_market_cap_impact"], item["ticker"]))


def estimate_buyer_impact(
    *,
    hyperscaler: str,
    capex_increment: float,
    hyperscaler_config: dict[str, Any],
    depreciation_years: int,
    scenario: str,
    scenario_assumptions: dict[str, float],
) -> dict[str, Any]:
    scenario_capex = capex_increment * float(scenario_assumptions.get("capex_multiplier", 1.0))
    annual_depreciation = scenario_capex / max(depreciation_years, 1)
    tax_rate = float(hyperscaler_config.get("tax_rate", 0.0))
    after_tax_depreciation_pressure = annual_depreciation * (1.0 - tax_rate)
    market_cap = float(hyperscaler_config.get("market_cap", 0.0))
    return {
        "scenario": scenario,
        "hyperscaler": hyperscaler,
        "fcf_pressure": round(-scenario_capex, 2),
        "annual_depreciation": round(annual_depreciation, 2),
        "after_tax_depreciation_pressure": round(after_tax_depreciation_pressure, 2),
        "market_cap": market_cap,
        "after_tax_depreciation_pressure_pct": round(after_tax_depreciation_pressure / market_cap, 6) if market_cap else 0.0,
        "confidence": float(scenario_assumptions.get("confidence", 0.6)),
        "source_type": SOURCE_MODEL_ESTIMATED,
        "note": "Buyer-side pressure estimate from incremental capex.",
    }


def estimate_capex_transmission(capex_config: dict[str, Any], event: dict[str, Any] | None = None) -> dict[str, Any]:
    capex_event = event or capex_config["default_event"]
    hyperscaler = capex_event["hyperscaler"]
    capex_increment = float(capex_event["capex_increment"])
    category_shares = capex_config["category_shares"]
    scenarios = capex_config.get("scenarios") or _default_scenarios()

    scenario_results: dict[str, dict[str, Any]] = {}
    for scenario in SCENARIO_ORDER:
        assumptions = scenarios.get(scenario, _default_scenarios()[scenario])
        category_rows = []
        for category, vendors in capex_config.get("vendors", {}).items():
            category_share = float(category_shares.get(category, 0.0))
            for vendor in vendors:
                category_rows.append(
                    estimate_vendor_impact(
                        hyperscaler=hyperscaler,
                        capex_increment=capex_increment,
                        category=category,
                        category_share=category_share,
                        vendor=vendor,
                        scenario=scenario,
                        scenario_assumptions=assumptions,
                    )
                )

        scenario_results[scenario] = {
            "buyer_impact": estimate_buyer_impact(
                hyperscaler=hyperscaler,
                capex_increment=capex_increment,
                hyperscaler_config=capex_config.get("hyperscalers", {}).get(hyperscaler, {}),
                depreciation_years=int(capex_config.get("depreciation_years", 5)),
                scenario=scenario,
                scenario_assumptions=assumptions,
            ),
            "category_impacts": category_rows,
            "ticker_impacts": _aggregate_ticker_impacts(category_rows),
        }

    return {
        "event": {
            **capex_event,
            "source_type": capex_event.get("source_type", "media_reported"),
        },
        "scenarios": scenario_results,
        "buyer_impact": scenario_results["base"]["buyer_impact"],
        "vendor_impacts": scenario_results["base"]["ticker_impacts"],
    }
