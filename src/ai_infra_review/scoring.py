from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .metrics import (
    SOURCE_MISSING,
    STATUS_CONFIRMED,
    STATUS_MISSING,
    clamp,
    is_usable_for_layer_scoring,
    metric_catalog_by_id,
    normalize_metric_point,
    score_from_thresholds,
    validate_metric_value,
    weighted_score,
)

MetricSnapshot = dict[str, Any]


DIMENSION_INDICATORS = {
    "demand_score": {
        "tsmc_monthly_revenue_growth",
        "data_center_revenue_growth",
        "hbm_price_trend",
        "storage_demand_growth",
        "ai_networking_order_growth",
        "cloud_revenue_growth",
        "reserve_need",
    },
    "supply_bottleneck_score": {
        "advanced_node_mix",
        "supply_bottleneck",
        "capex_discipline",
        "bottleneck_intensity",
        "portfolio_stress",
    },
    "margin_score": {
        "margin_trend",
        "gross_margin_trend",
        "server_margin_trend",
        "cloud_margin_trend",
        "fcf_after_capex_trend",
    },
    "valuation_score": {
        "valuation_risk",
    },
    "order_visibility_score": {
        "equipment_order_visibility",
        "ai_order_visibility",
        "power_cooling_backlog_growth",
        "rpo_backlog_growth",
    },
}

DIMENSION_WEIGHTS = {
    "demand_score": 0.25,
    "supply_bottleneck_score": 0.20,
    "margin_score": 0.20,
    "valuation_score": 0.20,
    "order_visibility_score": 0.15,
}


def score_indicator(
    indicator_name: str,
    metric: dict[str, Any] | None,
    indicator_config: dict[str, Any],
    *,
    ticker: str | None = None,
    layer: str | None = None,
    metric_spec: Any | None = None,
) -> dict[str, Any]:
    metric_point = (
        validate_metric_value(indicator_name, metric, metric_spec)
        if metric_spec
        else normalize_metric_point(metric)
    )
    weight = float(indicator_config.get("weight", 0.0))
    usable_for_scoring = (
        is_usable_for_layer_scoring(metric_point, metric_spec)
        if metric_spec
        else metric_point["source_type"] != SOURCE_MISSING
    )

    if usable_for_scoring:
        direction = indicator_config.get("direction", "positive")
        thresholds = indicator_config["thresholds"]
        metadata = metric_point.get("metadata", {})
        valuation_source_metric = metadata.get("valuation_source_metric")
        thresholds_by_metric = getattr(metric_spec, "thresholds_by_metric", None) if metric_spec else None
        if valuation_source_metric and thresholds_by_metric and valuation_source_metric in thresholds_by_metric:
            valuation_settings = thresholds_by_metric[valuation_source_metric]
            direction = valuation_settings.get("direction", direction)
            thresholds = valuation_settings.get("thresholds", thresholds)
        score = score_from_thresholds(
            value=float(metric_point["value"]),
            direction=direction,
            thresholds=thresholds,
        )
    else:
        score = None

    return {
        "scope": "indicator",
        "ticker": ticker,
        "layer": layer,
        "indicator": indicator_name,
        "label": indicator_config.get("label", indicator_name),
        "value": metric_point.get("value"),
        "source_type": metric_point["source_type"],
        "status": metric_point.get("status", STATUS_CONFIRMED if usable_for_scoring else STATUS_MISSING),
        "score": score,
        "weight": weight,
        "weighted_score": round(score * weight, 4) if score is not None else None,
        "note": metric_point.get("note", ""),
        "as_of": metric_point.get("as_of"),
        "unit": metric_point.get("unit"),
        "period": metric_point.get("period"),
        "confidence": metric_point.get("confidence"),
        "metadata": metric_point.get("metadata", {}),
        "usable_for_scoring": usable_for_scoring,
        "required_for_layer_score": bool(getattr(metric_spec, "required_for_layer_score", False)),
    }


def _reason_for_rows(rows: list[dict[str, Any]], dimension: str) -> str:
    if not rows:
        return f"{dimension} has no configured metric in this layer; neutral score used."
    missing = [row["indicator"] for row in rows if row.get("status") == STATUS_MISSING or row["source_type"] == SOURCE_MISSING]
    unusable = [
        row["indicator"]
        for row in rows
        if not row.get("usable_for_scoring") and row.get("status") not in {STATUS_MISSING, None}
    ]
    scored = [f"{row['indicator']}={row['score']}" for row in rows if row.get("usable_for_scoring")]
    parts = []
    if scored:
        parts.append("scored " + ", ".join(scored))
    if missing:
        parts.append("missing " + ", ".join(missing))
    if unusable:
        parts.append("not confirmed " + ", ".join(unusable))
    return "; ".join(parts) + "."


def score_company(
    company_snapshot: dict[str, Any],
    indicator_config: dict[str, Any],
    metric_catalog: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ticker = company_snapshot["ticker"]
    layer = company_snapshot["layer"]
    metrics = company_snapshot.get("metrics", {})
    layer_indicators = indicator_config["layers"][layer]
    specs = metric_catalog_by_id(metric_catalog)
    indicator_rows = [
        score_indicator(
            indicator_name=name,
            metric=metrics.get(name),
            indicator_config=settings,
            ticker=ticker,
            layer=layer,
            metric_spec=specs.get(name),
        )
        for name, settings in layer_indicators.items()
    ]
    score = weighted_score([row for row in indicator_rows if row.get("usable_for_scoring")])
    missing_count = sum(1 for row in indicator_rows if row.get("status") == STATUS_MISSING or row["source_type"] == SOURCE_MISSING)
    usable_count = sum(1 for row in indicator_rows if row.get("usable_for_scoring"))
    confirmed_metric_coverage = round(usable_count / len(indicator_rows), 4) if indicator_rows else 0.0
    return {
        "scope": "company",
        "ticker": ticker,
        "layer": layer,
        "score": score,
        "weighted_score": score,
        "missing_count": missing_count,
        "indicator_count": len(indicator_rows),
        "confirmed_metric_count": usable_count,
        "confirmed_metric_coverage": confirmed_metric_coverage,
        "score_status": "scored" if usable_count else "insufficient_data",
        "indicator_rows": indicator_rows,
        "source_type": "mixed",
        "note": company_snapshot.get("note", ""),
    }


@dataclass(frozen=True)
class LayerScoreCalculator:
    indicator_config: dict[str, Any]
    layers_config: list[dict[str, Any]]
    metric_catalog: dict[str, Any] | None = None
    quality_gates: dict[str, Any] | None = None

    def calculate(self, metric_snapshot: MetricSnapshot) -> list[dict[str, Any]]:
        company_scores = score_universe(metric_snapshot, self.indicator_config, self.metric_catalog)
        indicator_rows_by_layer: dict[str, list[dict[str, Any]]] = {}
        company_scores_by_layer: dict[str, list[dict[str, Any]]] = {}
        min_coverage = float((self.quality_gates or {}).get("min_confirmed_metric_coverage_for_scoring", 0.0))

        for company in company_scores:
            layer = company["layer"]
            company_scores_by_layer.setdefault(layer, []).append(company)
            indicator_rows_by_layer.setdefault(layer, []).extend(company["indicator_rows"])

        layer_scores = []
        for layer_config in self.layers_config:
            layer_id = layer_config["id"]
            indicator_rows = indicator_rows_by_layer.get(layer_id, [])
            layer_companies = company_scores_by_layer.get(layer_id, [])
            dimension_outputs: dict[str, Any] = {}
            total_inputs = []
            required_rows = [row for row in indicator_rows if row.get("required_for_layer_score")]
            coverage_rows = required_rows if required_rows else indicator_rows
            confirmed_count = sum(1 for row in coverage_rows if row.get("usable_for_scoring"))
            confirmed_metric_coverage = round(confirmed_count / len(coverage_rows), 4) if coverage_rows else 0.0
            insufficient_data = confirmed_metric_coverage < min_coverage

            if insufficient_data:
                for dimension in DIMENSION_INDICATORS:
                    dimension_outputs[dimension] = {
                        "score": 0.0,
                        "reason": "Insufficient confirmed metrics",
                    }
                total_score = 0.0
                score_status = "insufficient_data"
                layer_reason = "Insufficient confirmed metrics"
            else:
                for dimension, indicator_names in DIMENSION_INDICATORS.items():
                    rows = [row for row in indicator_rows if row["indicator"] in indicator_names]
                    usable_rows = [row for row in rows if row.get("usable_for_scoring")]
                    dimension_score = weighted_score(usable_rows) if usable_rows else 0.0
                    dimension_outputs[dimension] = {
                        "score": dimension_score,
                        "reason": _reason_for_rows(rows, dimension),
                    }
                    total_inputs.append({"score": dimension_score, "weight": DIMENSION_WEIGHTS[dimension]})

                total_score = weighted_score(total_inputs)
                score_status = "scored"
                layer_reason = "Total score is the weighted blend of demand, bottleneck, margin, valuation, and order visibility."

            missing_count = sum(1 for row in indicator_rows if row.get("status") == STATUS_MISSING or row["source_type"] == SOURCE_MISSING)
            layer_scores.append(
                {
                    "scope": "layer",
                    "ticker": "",
                    "layer": layer_id,
                    "layer_name": layer_config["name"],
                    "demand_score": dimension_outputs["demand_score"]["score"],
                    "demand_reason": dimension_outputs["demand_score"]["reason"],
                    "supply_bottleneck_score": dimension_outputs["supply_bottleneck_score"]["score"],
                    "supply_bottleneck_reason": dimension_outputs["supply_bottleneck_score"]["reason"],
                    "margin_score": dimension_outputs["margin_score"]["score"],
                    "margin_reason": dimension_outputs["margin_score"]["reason"],
                    "valuation_score": dimension_outputs["valuation_score"]["score"],
                    "valuation_reason": dimension_outputs["valuation_score"]["reason"],
                    "order_visibility_score": dimension_outputs["order_visibility_score"]["score"],
                    "order_visibility_reason": dimension_outputs["order_visibility_score"]["reason"],
                    "total_score": total_score,
                    "score": total_score,
                    "weighted_score": total_score,
                    "reason": layer_reason,
                    "score_status": score_status,
                    "confirmed_metric_coverage": confirmed_metric_coverage,
                    "confirmed_metric_count": confirmed_count,
                    "required_metric_count": len(coverage_rows),
                    "missing_count": missing_count,
                    "company_count": len(layer_companies),
                    "target_weight": layer_config.get("target_weight", 0.0),
                    "max_weight": layer_config.get("max_weight", 0.0),
                    "source_type": "mixed" if layer_companies else SOURCE_MISSING,
                    "note": "",
                }
            )
        return layer_scores


def score_universe(
    metric_snapshot: dict[str, Any],
    indicator_config: dict[str, Any],
    metric_catalog: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return [
        score_company(company_snapshot, indicator_config, metric_catalog)
        for company_snapshot in metric_snapshot.get("companies", [])
        if company_snapshot.get("layer") in indicator_config.get("layers", {})
    ]


def score_layers(
    company_scores: list[dict[str, Any]],
    layers_config: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    scores_by_layer: dict[str, list[dict[str, Any]]] = {}
    for company in company_scores:
        scores_by_layer.setdefault(company["layer"], []).append(company)

    layer_rows = []
    for layer in layers_config:
        layer_id = layer["id"]
        companies = scores_by_layer.get(layer_id, [])
        if companies:
            score = round(clamp(sum(float(company["score"]) for company in companies) / len(companies)), 4)
            missing_count = sum(int(company.get("missing_count", 0)) for company in companies)
        else:
            score = 0.0
            missing_count = 0
        layer_rows.append(
            {
                "scope": "layer",
                "ticker": "",
                "layer": layer_id,
                "layer_name": layer["name"],
                "score": score,
                "total_score": score,
                "demand_score": score,
                "demand_reason": "Legacy layer score call used company-score average.",
                "supply_bottleneck_score": score,
                "supply_bottleneck_reason": "Legacy layer score call used company-score average.",
                "margin_score": score,
                "margin_reason": "Legacy layer score call used company-score average.",
                "valuation_score": score,
                "valuation_reason": "Legacy layer score call used company-score average.",
                "order_visibility_score": score,
                "order_visibility_reason": "Legacy layer score call used company-score average.",
                "reason": "Legacy layer score call used company-score average.",
                "score_status": "scored" if companies else "insufficient_data",
                "confirmed_metric_coverage": 1.0 if companies else 0.0,
                "weighted_score": score,
                "missing_count": missing_count,
                "company_count": len(companies),
                "target_weight": layer.get("target_weight", 0.0),
                "max_weight": layer.get("max_weight", 0.0),
                "source_type": "mixed" if companies else SOURCE_MISSING,
                "note": "",
            }
        )
    return layer_rows


def flatten_score_rows(company_scores: list[dict[str, Any]], layer_scores: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for layer in layer_scores:
        rows.append(layer)
    for company in company_scores:
        rows.append({key: value for key, value in company.items() if key != "indicator_rows"})
        rows.extend(company["indicator_rows"])
    return rows


def rank_company_scores(company_scores: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(company_scores, key=lambda row: (-float(row["score"]), row["ticker"]))
