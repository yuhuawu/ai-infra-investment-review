from ai_infra_review.rebalance import adjusted_layer_targets, propose_rebalance


def test_adjusted_layer_targets_respect_cash_and_layer_caps():
    layers = [
        {"id": "L2", "target_weight": 0.28, "max_weight": 0.30},
        {"id": "L6", "target_weight": 0.05, "max_weight": 0.15},
    ]
    layer_scores = [{"layer": "L2", "total_score": 2.0}]

    targets = adjusted_layer_targets(layers, layer_scores, min_cash_weight=0.05)

    assert targets["L2"] == 0.3
    assert targets["L6"] == 0.7


def test_propose_rebalance_suppresses_small_changes():
    proposals = propose_rebalance(
        holdings=[
            {"ticker": "AAA", "layer": "L2", "current_weight": 0.10, "risk_bucket": "core"},
            {"ticker": "CASH", "layer": "L6", "current_weight": 0.90, "risk_bucket": "cash"},
        ],
        layers=[
            {"id": "L2", "target_weight": 0.10, "max_weight": 0.20},
            {"id": "L6", "target_weight": 0.90, "max_weight": 1.0},
        ],
        layer_scores=[{"layer": "L2", "total_score": 0.0}, {"layer": "L6", "total_score": 0.0}],
        company_scores=[{"ticker": "AAA", "layer": "L2", "score": 0.0, "missing_count": 0}],
        constraints={"min_cash_weight": 0.90, "rebalance_band": 0.02, "min_trade_delta": 0.01, "max_single_stock_weight": 0.20},
    )

    assert proposals[0]["delta_weight"] == 0.0
    assert "inside_rebalance_band" in proposals[0]["constraint_flags"]


def test_propose_rebalance_flags_missing_heavy_names_as_watch_constraint():
    proposals = propose_rebalance(
        holdings=[
            {"ticker": "AAA", "layer": "L2", "current_weight": 0.05, "risk_bucket": "core"},
            {"ticker": "CASH", "layer": "L6", "current_weight": 0.95, "risk_bucket": "cash"},
        ],
        layers=[
            {"id": "L2", "target_weight": 0.20, "max_weight": 0.30},
            {"id": "L6", "target_weight": 0.05, "max_weight": 1.0},
        ],
        layer_scores=[{"layer": "L2", "total_score": 1.0}, {"layer": "L6", "total_score": 0.0}],
        company_scores=[{"ticker": "AAA", "layer": "L2", "score": 1.0, "missing_count": 2}],
        constraints={"min_cash_weight": 0.05, "rebalance_band": 0.02, "min_trade_delta": 0.01, "max_single_stock_weight": 0.30},
    )

    assert "missing_data" in proposals[0]["constraint_flags"]
    assert proposals[0]["confidence"] < 0.8


def test_propose_rebalance_respects_single_stock_and_cash_constraints():
    proposals = propose_rebalance(
        holdings=[
            {"ticker": "AAA", "layer": "L2", "current_weight": 0.10, "risk_bucket": "core"},
            {"ticker": "CASH", "layer": "L6", "current_weight": 0.90, "risk_bucket": "cash"},
        ],
        layers=[
            {"id": "L2", "target_weight": 0.50, "max_weight": 0.80},
            {"id": "L6", "target_weight": 0.05, "max_weight": 1.0},
        ],
        layer_scores=[{"layer": "L2", "total_score": 2.0}, {"layer": "L6", "total_score": 0.0}],
        company_scores=[{"ticker": "AAA", "layer": "L2", "score": 2.0, "missing_count": 0}],
        constraints={"min_cash_weight": 0.25, "rebalance_band": 0.02, "min_trade_delta": 0.01, "max_single_stock_weight": 0.18},
    )

    by_ticker = {row["ticker"]: row for row in proposals}
    assert by_ticker["AAA"]["proposed_weight"] == 0.18
    assert "max_single_stock_weight" in by_ticker["AAA"]["constraint_flags"]
    assert by_ticker["CASH"]["proposed_weight"] >= 0.25
