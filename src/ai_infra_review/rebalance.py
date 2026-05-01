from __future__ import annotations

from typing import Any


def _constraint(constraints: dict[str, Any], primary: str, fallback: str, default: float) -> float:
    return float(constraints.get(primary, constraints.get(fallback, default)))


def _layer_score_value(row: dict[str, Any]) -> float:
    return float(row.get("total_score", row.get("score", 0.0)))


def _all_scores_zero_due_insufficient_data(layer_scores: list[dict[str, Any]]) -> bool:
    if not layer_scores:
        return True
    return all(
        _layer_score_value(row) == 0.0 and row.get("score_status") == "insufficient_data"
        for row in layer_scores
    )


def adjusted_layer_targets(
    layers: list[dict[str, Any]],
    layer_scores: list[dict[str, Any]],
    min_cash_weight: float,
) -> dict[str, float]:
    score_by_layer = {row["layer"]: _layer_score_value(row) for row in layer_scores}
    targets = {}

    for layer in layers:
        layer_id = layer["id"]
        base = float(layer.get("target_weight", 0.0))
        if layer_id == "L6":
            continue
        adjustment = score_by_layer.get(layer_id, 0.0) * 0.025
        targets[layer_id] = max(0.0, min(float(layer.get("max_weight", base)), base + adjustment))

    investable = max(0.0, 1.0 - min_cash_weight)
    non_cash_total = sum(targets.values())
    if non_cash_total > investable and non_cash_total > 0:
        scale = investable / non_cash_total
        targets = {layer_id: weight * scale for layer_id, weight in targets.items()}
    targets["L6"] = max(min_cash_weight, 1.0 - sum(targets.values()))
    return {layer_id: round(weight, 4) for layer_id, weight in targets.items()}


def _confidence(score: float, missing_count: int, constraint_flags: list[str]) -> float:
    confidence = 0.75
    confidence += min(abs(score), 2.0) * 0.05
    confidence -= min(missing_count, 4) * 0.10
    confidence -= len(constraint_flags) * 0.05
    return round(max(0.20, min(0.95, confidence)), 2)


def _missing_valuation_by_ticker(company_scores: list[dict[str, Any]]) -> set[str]:
    tickers = set()
    for company in company_scores:
        for row in company.get("indicator_rows", []):
            if row.get("indicator") == "valuation_risk" and not row.get("usable_for_scoring"):
                tickers.add(company["ticker"])
    return tickers


def _no_action_proposals(
    holdings: list[dict[str, Any]],
    layer_scores: list[dict[str, Any]],
    company_scores: list[dict[str, Any]],
    reason: str,
) -> list[dict[str, Any]]:
    layer_status = {row["layer"]: row.get("score_status") for row in layer_scores}
    missing_valuation = _missing_valuation_by_ticker(company_scores)
    proposals = []
    for holding in holdings:
        ticker = holding["ticker"]
        layer = holding["layer"]
        current = round(float(holding.get("current_weight", 0.0)), 4)
        flags = ["dry_run_only"]
        if layer_status.get(layer) == "insufficient_data":
            flags.append("insufficient_data")
        if layer not in layer_status:
            flags.append("missing_layer_score")
        if ticker in missing_valuation:
            flags.append("missing_valuation")
        proposals.append(
            {
                "ticker": ticker,
                "layer": layer,
                "action": "no_action",
                "current_weight": current,
                "proposed_weight": current,
                "delta_weight": 0.0,
                "reason": reason,
                "confidence": 0.2,
                "constraint_flags": ";".join(dict.fromkeys(flags)),
            }
        )
    return proposals


def _target_weights_by_holding(
    holdings: list[dict[str, Any]],
    layer_targets: dict[str, float],
    company_scores: list[dict[str, Any]],
    constraints: dict[str, Any],
) -> dict[str, float]:
    scores = {row["ticker"]: float(row["score"]) for row in company_scores}
    holdings_by_layer: dict[str, list[dict[str, Any]]] = {}
    for holding in holdings:
        holdings_by_layer.setdefault(holding["layer"], []).append(holding)

    targets = {}
    max_single_stock_weight = _constraint(constraints, "max_single_stock_weight", "max_single_position", 1.0)
    max_high_risk_position = float(constraints.get("max_high_risk_position", max_single_stock_weight))

    for layer, layer_holdings in holdings_by_layer.items():
        layer_target = layer_targets.get(layer, 0.0)
        if layer == "L6":
            for holding in layer_holdings:
                targets[holding["ticker"]] = layer_target
            continue

        eligible = [
            holding
            for holding in layer_holdings
            if scores.get(holding["ticker"], 0.0) >= -0.5
        ]
        if not eligible:
            for holding in layer_holdings:
                targets[holding["ticker"]] = 0.0
            continue

        score_basis = {
            holding["ticker"]: max(scores.get(holding["ticker"], 0.0) + 2.0, 0.1)
            for holding in eligible
        }
        basis_total = sum(score_basis.values())

        capped_total = 0.0
        uncapped: list[tuple[dict[str, Any], float, float]] = []
        for holding in layer_holdings:
            ticker = holding["ticker"]
            if ticker not in score_basis:
                targets[ticker] = 0.0
                continue
            raw = layer_target * score_basis[ticker] / basis_total
            cap = max_single_stock_weight
            if holding.get("risk_bucket") == "high_risk":
                cap = min(cap, max_high_risk_position)
            if raw >= cap:
                targets[ticker] = cap
                capped_total += cap
            else:
                uncapped.append((holding, raw, cap))

        uncapped_total = sum(raw for _, raw, _ in uncapped)
        remaining = max(0.0, layer_target - capped_total)
        scale = remaining / uncapped_total if uncapped_total > 0 else 0.0
        for holding, raw, cap in uncapped:
            targets[holding["ticker"]] = min(cap, raw * scale)

    return {ticker: round(weight, 4) for ticker, weight in targets.items()}


def propose_rebalance(
    holdings: list[dict[str, Any]],
    layers: list[dict[str, Any]],
    layer_scores: list[dict[str, Any]],
    company_scores: list[dict[str, Any]],
    constraints: dict[str, Any],
) -> list[dict[str, Any]]:
    min_cash_weight = _constraint(constraints, "min_cash_weight", "cash_buffer", 0.05)
    min_coverage = float(constraints.get("min_confirmed_metric_coverage_for_rebalance", 0.0))
    allow_all_zero = bool(constraints.get("allow_rebalance_when_all_scores_zero", True))
    missing_data_action = constraints.get("missing_data_action", "no_action")
    if (
        missing_data_action == "no_action"
        and not allow_all_zero
        and _all_scores_zero_due_insufficient_data(layer_scores)
    ):
        return _no_action_proposals(
            holdings,
            layer_scores,
            company_scores,
            "No action: insufficient confirmed metric coverage.",
        )

    layer_targets = adjusted_layer_targets(
        layers=layers,
        layer_scores=layer_scores,
        min_cash_weight=min_cash_weight,
    )
    proposed_weights = _target_weights_by_holding(holdings, layer_targets, company_scores, constraints)
    score_by_ticker = {row["ticker"]: float(row["score"]) for row in company_scores}
    missing_by_ticker = {row["ticker"]: int(row.get("missing_count", 0)) for row in company_scores}
    rebalance_band = float(constraints.get("rebalance_band", 0.02))
    min_trade_delta = float(constraints.get("min_trade_delta", 0.01))
    max_single_stock_weight = _constraint(constraints, "max_single_stock_weight", "max_single_position", 1.0)
    max_high_risk_position = float(constraints.get("max_high_risk_position", max_single_stock_weight))
    layer_status = {row["layer"]: row.get("score_status") for row in layer_scores}
    layer_coverage = {row["layer"]: float(row.get("confirmed_metric_coverage", 1.0)) for row in layer_scores}
    missing_valuation = _missing_valuation_by_ticker(company_scores)

    proposals = []
    for holding in holdings:
        ticker = holding["ticker"]
        layer = holding["layer"]
        current = float(holding.get("current_weight", 0.0))
        proposed = proposed_weights.get(ticker, 0.0)
        delta = round(proposed - current, 4)
        score = score_by_ticker.get(ticker, 0.0)
        missing_count = missing_by_ticker.get(ticker, 0)
        constraint_flags: list[str] = ["dry_run_only"]

        if layer == "L6" and proposed < min_cash_weight:
            constraint_flags.append("min_cash_weight")
            proposed = min_cash_weight
            delta = round(proposed - current, 4)
        if layer not in layer_status:
            constraint_flags.append("missing_layer_score")
        if layer_status.get(layer) == "insufficient_data" or layer_coverage.get(layer, 0.0) < min_coverage:
            constraint_flags.append("insufficient_data")
            proposed = current
            delta = 0.0
        if ticker in missing_valuation:
            constraint_flags.append("missing_valuation")
        if proposed >= max_single_stock_weight and layer != "L6":
            constraint_flags.append("max_single_stock_weight")
        if holding.get("risk_bucket") == "high_risk":
            constraint_flags.append("high_risk_position")
            if proposed >= max_high_risk_position:
                constraint_flags.append("max_high_risk_position")
        if missing_count >= 2:
            constraint_flags.append("missing_data")
        if abs(delta) < max(rebalance_band, min_trade_delta):
            constraint_flags.append("inside_rebalance_band")

        if "insufficient_data" in constraint_flags:
            direction = "no_action"
        elif abs(delta) < max(rebalance_band, min_trade_delta):
            direction = "hold"
        elif delta > 0:
            direction = "increase"
        else:
            direction = "decrease"

        reason = (
            f"{direction} proposal; layer_target={layer_targets.get(layer, 0.0):.2%}; "
            f"score={score:.2f}; missing_metrics={missing_count}"
        )

        proposals.append(
            {
                "ticker": ticker,
                "layer": layer,
                "action": direction,
                "current_weight": round(current, 4),
                "proposed_weight": round(proposed, 4),
                "delta_weight": delta,
                "reason": reason,
                "confidence": _confidence(score, missing_count, constraint_flags),
                "constraint_flags": ";".join(dict.fromkeys(constraint_flags)),
            }
        )
    return proposals
