from __future__ import annotations

from datetime import date
from typing import Any


def _metric(value: float | None, source_type: str, note: str) -> dict[str, Any]:
    evidence_text = None if source_type == "missing" else note
    return {
        "value": value,
        "source_type": source_type,
        "as_of": date.today().isoformat(),
        "period": date.today().isoformat(),
        "source_id": "mock_snapshot",
        "evidence_text": evidence_text,
        "confidence": 0.80 if value is not None else 0.0,
        "note": note,
    }


def load_mock_metric_snapshot() -> dict[str, Any]:
    return {
        "as_of": date.today().isoformat(),
        "companies": [
            {
                "ticker": "TSM",
                "layer": "L1",
                "metrics": {
                    "tsmc_monthly_revenue_growth": _metric(0.36, "company_disclosed", "Mock monthly revenue growth."),
                    "advanced_node_mix": _metric(0.74, "company_disclosed", "Mock advanced node share."),
                    "equipment_order_visibility": _metric(0.12, "analyst_estimated", "Mock equipment order proxy."),
                    "valuation_risk": _metric(0.42, "analyst_estimated", "Mock valuation risk percentile."),
                    "margin_trend": _metric(0.04, "company_disclosed", "Mock margin trend."),
                },
            },
            {
                "ticker": "ASML",
                "layer": "L1",
                "metrics": {
                    "tsmc_monthly_revenue_growth": _metric(0.30, "company_disclosed", "Mock demand proxy."),
                    "advanced_node_mix": _metric(0.68, "analyst_estimated", "Mock advanced node proxy."),
                    "equipment_order_visibility": _metric(0.18, "company_disclosed", "Mock order visibility."),
                    "valuation_risk": _metric(0.48, "analyst_estimated", "Mock valuation risk percentile."),
                    "margin_trend": _metric(None, "missing", "No mock margin update."),
                },
            },
            {
                "ticker": "NVDA",
                "layer": "L2",
                "metrics": {
                    "data_center_revenue_growth": _metric(0.75, "company_disclosed", "Mock data center growth."),
                    "ai_order_visibility": _metric(0.45, "company_disclosed", "Mock order visibility."),
                    "gross_margin_trend": _metric(0.02, "company_disclosed", "Mock gross margin trend."),
                    "valuation_risk": _metric(0.78, "analyst_estimated", "Mock valuation risk percentile."),
                    "supply_bottleneck": _metric(0.82, "media_reported", "Mock supply bottleneck signal."),
                },
            },
            {
                "ticker": "AVGO",
                "layer": "L2",
                "metrics": {
                    "data_center_revenue_growth": _metric(0.42, "company_disclosed", "Mock AI semiconductor growth."),
                    "ai_order_visibility": _metric(0.35, "company_disclosed", "Mock custom silicon visibility."),
                    "gross_margin_trend": _metric(0.01, "company_disclosed", "Mock margin trend."),
                    "valuation_risk": _metric(0.58, "analyst_estimated", "Mock valuation risk percentile."),
                    "supply_bottleneck": _metric(0.62, "analyst_estimated", "Mock ASIC bottleneck signal."),
                },
            },
            {
                "ticker": "AMD",
                "layer": "L2",
                "metrics": {
                    "data_center_revenue_growth": _metric(0.28, "company_disclosed", "Mock data center growth."),
                    "ai_order_visibility": _metric(0.14, "analyst_estimated", "Mock Instinct order visibility."),
                    "gross_margin_trend": _metric(-0.01, "company_disclosed", "Mock margin trend."),
                    "valuation_risk": _metric(0.52, "analyst_estimated", "Mock valuation risk percentile."),
                    "supply_bottleneck": _metric(None, "missing", "No reliable mock supply read-through."),
                },
            },
            {
                "ticker": "MU",
                "layer": "L3",
                "metrics": {
                    "hbm_price_trend": _metric(0.22, "analyst_estimated", "Mock HBM price trend."),
                    "storage_demand_growth": _metric(0.18, "company_disclosed", "Mock storage demand."),
                    "margin_trend": _metric(0.07, "company_disclosed", "Mock margin recovery."),
                    "capex_discipline": _metric(0.70, "company_disclosed", "Mock capex discipline signal."),
                    "valuation_risk": _metric(0.36, "analyst_estimated", "Mock valuation risk percentile."),
                },
            },
            {
                "ticker": "STX",
                "layer": "L3",
                "metrics": {
                    "hbm_price_trend": _metric(0.08, "analyst_estimated", "Mock memory proxy."),
                    "storage_demand_growth": _metric(0.30, "company_disclosed", "Mock nearline demand."),
                    "margin_trend": _metric(0.09, "company_disclosed", "Mock margin trend."),
                    "capex_discipline": _metric(0.62, "analyst_estimated", "Mock capex discipline."),
                    "valuation_risk": _metric(None, "missing", "No mock valuation risk value."),
                },
            },
            {
                "ticker": "ANET",
                "layer": "L4",
                "metrics": {
                    "ai_networking_order_growth": _metric(0.32, "company_disclosed", "Mock AI networking orders."),
                    "power_cooling_backlog_growth": _metric(0.10, "analyst_estimated", "Not a direct ANET metric; proxy only."),
                    "server_margin_trend": _metric(0.02, "company_disclosed", "Mock margin trend."),
                    "valuation_risk": _metric(0.62, "analyst_estimated", "Mock valuation risk percentile."),
                    "bottleneck_intensity": _metric(0.68, "media_reported", "Mock Ethernet bottleneck signal."),
                },
            },
            {
                "ticker": "VRT",
                "layer": "L4",
                "metrics": {
                    "ai_networking_order_growth": _metric(0.12, "analyst_estimated", "Indirect AI infra demand proxy."),
                    "power_cooling_backlog_growth": _metric(1.09, "company_disclosed", "Mock backlog growth."),
                    "server_margin_trend": _metric(0.04, "company_disclosed", "Mock margin trend."),
                    "valuation_risk": _metric(0.66, "analyst_estimated", "Mock valuation risk percentile."),
                    "bottleneck_intensity": _metric(0.85, "company_disclosed", "Mock physical bottleneck signal."),
                },
            },
            {
                "ticker": "MSFT",
                "layer": "L5",
                "metrics": {
                    "cloud_revenue_growth": _metric(0.29, "company_disclosed", "Mock cloud growth."),
                    "rpo_backlog_growth": _metric(0.36, "company_disclosed", "Mock RPO growth."),
                    "cloud_margin_trend": _metric(-0.02, "company_disclosed", "Mock AI infrastructure margin pressure."),
                    "fcf_after_capex_trend": _metric(-0.04, "analyst_estimated", "Mock FCF after capex trend."),
                    "valuation_risk": _metric(0.44, "analyst_estimated", "Mock valuation risk percentile."),
                },
            },
            {
                "ticker": "GOOGL",
                "layer": "L5",
                "metrics": {
                    "cloud_revenue_growth": _metric(0.32, "company_disclosed", "Mock cloud growth."),
                    "rpo_backlog_growth": _metric(0.52, "company_disclosed", "Mock backlog growth."),
                    "cloud_margin_trend": _metric(0.02, "company_disclosed", "Mock cloud margin trend."),
                    "fcf_after_capex_trend": _metric(0.01, "analyst_estimated", "Mock FCF after capex trend."),
                    "valuation_risk": _metric(0.38, "analyst_estimated", "Mock valuation risk percentile."),
                },
            },
            {
                "ticker": "META",
                "layer": "L5",
                "metrics": {
                    "cloud_revenue_growth": _metric(0.18, "company_disclosed", "Mock AI monetization proxy."),
                    "rpo_backlog_growth": _metric(0.18, "media_reported", "Mock AI infrastructure commitment proxy."),
                    "cloud_margin_trend": _metric(0.01, "company_disclosed", "Mock operating leverage proxy."),
                    "fcf_after_capex_trend": _metric(-0.12, "analyst_estimated", "Mock capex pressure."),
                    "valuation_risk": _metric(0.34, "analyst_estimated", "Mock valuation risk percentile."),
                },
            },
            {
                "ticker": "CRWV",
                "layer": "L5",
                "metrics": {
                    "cloud_revenue_growth": _metric(0.85, "company_disclosed", "Mock high-growth AI cloud revenue."),
                    "rpo_backlog_growth": _metric(None, "missing", "No mock RPO value."),
                    "cloud_margin_trend": _metric(-0.08, "company_disclosed", "Mock margin pressure."),
                    "fcf_after_capex_trend": _metric(-0.30, "analyst_estimated", "Mock FCF pressure."),
                    "valuation_risk": _metric(0.90, "analyst_estimated", "Mock valuation risk percentile."),
                },
            },
            {
                "ticker": "CASH",
                "layer": "L6",
                "metrics": {
                    "reserve_need": _metric(0.60, "model_estimated", "Mock reserve need from portfolio volatility."),
                    "portfolio_stress": _metric(0.45, "model_estimated", "Mock portfolio stress estimate."),
                },
            },
        ],
    }


def load_mock_company_metrics() -> dict[str, dict[str, float]]:
    snapshot = load_mock_metric_snapshot()
    return {
        company["ticker"]: {
            name: metric["value"]
            for name, metric in company.get("metrics", {}).items()
            if metric.get("value") is not None
        }
        for company in snapshot["companies"]
    }
