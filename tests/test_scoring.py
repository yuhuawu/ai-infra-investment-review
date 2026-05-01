from ai_infra_review.scoring import LayerScoreCalculator, score_indicator, score_layers, score_universe


def test_score_indicator_maps_positive_thresholds():
    config = {
        "weight": 1.0,
        "direction": "positive",
        "thresholds": {"plus2": 0.50, "plus1": 0.20, "minus1": -0.10, "minus2": -0.25},
    }

    assert score_indicator("growth", {"value": 0.60, "source_type": "company_disclosed"}, config)["score"] == 2
    assert score_indicator("growth", {"value": -0.30, "source_type": "company_disclosed"}, config)["score"] == -2


def test_score_indicator_maps_negative_thresholds():
    config = {
        "weight": 1.0,
        "direction": "negative",
        "thresholds": {"plus2": 0.10, "plus1": 0.25, "minus1": 0.65, "minus2": 0.85},
    }

    assert score_indicator("risk", {"value": 0.08, "source_type": "analyst_estimated"}, config)["score"] == 2
    assert score_indicator("risk", {"value": 0.90, "source_type": "analyst_estimated"}, config)["score"] == -2


def test_missing_indicator_is_not_zero_valued_and_preserves_source_type():
    config = {
        "weight": 1.0,
        "direction": "positive",
        "thresholds": {"plus2": 0.50, "plus1": 0.20, "minus1": -0.10, "minus2": -0.25},
    }

    row = score_indicator("growth", {"value": None, "source_type": "missing"}, config)

    assert row["score"] is None
    assert row["source_type"] == "missing"


def test_layer_score_is_weighted_and_clamped_legacy_path():
    indicators = {
        "layers": {
            "L2": {
                "growth": {
                    "weight": 0.5,
                    "direction": "positive",
                    "thresholds": {"plus2": 0.50, "plus1": 0.20, "minus1": -0.10, "minus2": -0.25},
                },
                "risk": {
                    "weight": 0.5,
                    "direction": "negative",
                    "thresholds": {"plus2": 0.10, "plus1": 0.25, "minus1": 0.65, "minus2": 0.85},
                },
            }
        }
    }
    snapshot = {
        "companies": [
            {
                "ticker": "AAA",
                "layer": "L2",
                "metrics": {
                    "growth": {"value": 0.60, "source_type": "company_disclosed"},
                    "risk": {"value": 0.08, "source_type": "analyst_estimated"},
                },
            }
        ]
    }

    company_scores = score_universe(snapshot, indicators)
    layer_scores = score_layers(company_scores, [{"id": "L2", "name": "Layer 2", "target_weight": 0.2, "max_weight": 0.3}])

    assert company_scores[0]["score"] == 2.0
    assert layer_scores[0]["score"] == 2.0


def test_layer_score_calculator_outputs_dimensions_and_reasons():
    indicators = {
        "layers": {
            "L2": {
                "data_center_revenue_growth": {
                    "weight": 1.0,
                    "direction": "positive",
                    "thresholds": {"plus2": 0.50, "plus1": 0.20, "minus1": -0.10, "minus2": -0.25},
                },
                "supply_bottleneck": {
                    "weight": 1.0,
                    "direction": "positive",
                    "thresholds": {"plus2": 0.80, "plus1": 0.55, "minus1": 0.25, "minus2": 0.10},
                },
                "gross_margin_trend": {
                    "weight": 1.0,
                    "direction": "positive",
                    "thresholds": {"plus2": 0.05, "plus1": 0.01, "minus1": -0.02, "minus2": -0.06},
                },
                "valuation_risk": {
                    "weight": 1.0,
                    "direction": "negative",
                    "thresholds": {"plus2": 0.10, "plus1": 0.25, "minus1": 0.65, "minus2": 0.85},
                },
                "ai_order_visibility": {
                    "weight": 1.0,
                    "direction": "positive",
                    "thresholds": {"plus2": 0.40, "plus1": 0.15, "minus1": -0.05, "minus2": -0.20},
                },
            }
        }
    }
    snapshot = {
        "companies": [
            {
                "ticker": "AAA",
                "layer": "L2",
                "metrics": {
                    "data_center_revenue_growth": {"value": 0.60, "source_type": "company_disclosed"},
                    "supply_bottleneck": {"value": None, "source_type": "missing"},
                    "gross_margin_trend": {"value": -0.08, "source_type": "company_disclosed"},
                    "valuation_risk": {"value": 0.90, "source_type": "analyst_estimated"},
                    "ai_order_visibility": {"value": 0.50, "source_type": "company_disclosed"},
                },
            }
        ]
    }

    rows = LayerScoreCalculator(indicators, [{"id": "L2", "name": "Layer 2", "target_weight": 0.2, "max_weight": 0.3}]).calculate(snapshot)
    row = rows[0]

    assert row["demand_score"] == 2.0
    assert row["supply_bottleneck_score"] == 0.0
    assert row["margin_score"] == -2.0
    assert row["valuation_score"] == -2.0
    assert row["order_visibility_score"] == 2.0
    assert -2.0 <= row["total_score"] <= 2.0
    assert "missing supply_bottleneck" in row["supply_bottleneck_reason"]
