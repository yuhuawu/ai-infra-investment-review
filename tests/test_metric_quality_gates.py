from ai_infra_review.metrics import MetricSpec, validate_metric_candidates, validate_metric_value
from ai_infra_review.rebalance import propose_rebalance
from ai_infra_review.scoring import LayerScoreCalculator, score_indicator


def _spec(**overrides):
    row = {
        "metric_id": "data_center_revenue_growth",
        "layer": "L2",
        "applicable_tickers": ["AAA"],
        "definition": "growth",
        "unit": "ratio",
        "period_type": "quarterly",
        "preferred_source_types": ["company_disclosed"],
        "accepted_source_types": ["company_disclosed", "model_estimated"],
        "validator": {"min": -1.0, "max": 5.0},
        "scoring_usage": "demand_score",
        "required_for_layer_score": True,
        "allow_model_estimated_for_layer_scoring": False,
    }
    row.update(overrides)
    return MetricSpec.from_dict(row)


def _indicator_config():
    return {
        "weight": 1.0,
        "direction": "positive",
        "thresholds": {"plus2": 0.50, "plus1": 0.20, "minus1": -0.10, "minus2": -0.25},
    }


def _confirmed_metric(value=0.60, source_type="company_disclosed"):
    return {
        "value": value,
        "unit": "ratio",
        "period": "2026Q1",
        "period_type": "quarterly",
        "source_type": source_type,
        "source_id": "fixture-10q",
        "evidence_text": "Data center revenue increased in the period.",
        "confidence": 0.9,
    }


def test_missing_metric_does_not_become_zero_valued_metric():
    row = score_indicator(
        "data_center_revenue_growth",
        {"value": None, "source_type": "missing"},
        _indicator_config(),
        metric_spec=_spec(),
    )

    assert row["value"] is None
    assert row["score"] is None
    assert row["status"] == "missing"


def test_all_missing_metrics_produce_insufficient_data_layer_status():
    indicators = {"layers": {"L2": {"data_center_revenue_growth": _indicator_config()}}}
    catalog = {"metrics": [_spec().__dict__]}
    snapshot = {
        "companies": [
            {
                "ticker": "AAA",
                "layer": "L2",
                "metrics": {"data_center_revenue_growth": {"value": None, "source_type": "missing"}},
            }
        ]
    }

    rows = LayerScoreCalculator(
        indicators,
        [{"id": "L2", "name": "Layer 2", "target_weight": 0.2, "max_weight": 0.3}],
        catalog,
        {"min_confirmed_metric_coverage_for_scoring": 0.60},
    ).calculate(snapshot)

    assert rows[0]["total_score"] == 0.0
    assert rows[0]["score_status"] == "insufficient_data"
    assert rows[0]["reason"] == "Insufficient confirmed metrics"


def test_insufficient_data_prevents_actionable_rebalance():
    proposals = propose_rebalance(
        holdings=[{"ticker": "AAA", "layer": "L2", "current_weight": 0.12, "risk_bucket": "core"}],
        layers=[{"id": "L2", "target_weight": 0.20, "max_weight": 0.30}],
        layer_scores=[
            {
                "layer": "L2",
                "total_score": 0.0,
                "score_status": "insufficient_data",
                "confirmed_metric_coverage": 0.0,
            }
        ],
        company_scores=[{"ticker": "AAA", "layer": "L2", "score": 0.0, "missing_count": 1}],
        constraints={
            "min_confirmed_metric_coverage_for_rebalance": 0.60,
            "allow_rebalance_when_all_scores_zero": False,
            "missing_data_action": "no_action",
        },
    )

    assert proposals[0]["action"] == "no_action"
    assert proposals[0]["proposed_weight"] == 0.12
    assert "insufficient_data" in proposals[0]["constraint_flags"]
    assert "dry_run_only" in proposals[0]["constraint_flags"]


def test_model_estimated_metrics_are_excluded_from_normal_scoring():
    row = score_indicator(
        "data_center_revenue_growth",
        _confirmed_metric(0.60, source_type="model_estimated"),
        _indicator_config(),
        metric_spec=_spec(),
    )

    assert row["status"] == "validated"
    assert row["score"] is None
    assert row["usable_for_scoring"] is False


def test_confirmed_metric_with_evidence_is_accepted():
    metric = validate_metric_value("data_center_revenue_growth", _confirmed_metric(), _spec())

    assert metric["status"] == "confirmed"
    assert metric["value"] == 0.60


def test_conflicting_metrics_are_flagged_as_conflict():
    metric = validate_metric_candidates(
        "data_center_revenue_growth",
        [_confirmed_metric(0.60), _confirmed_metric(0.30)],
        _spec(),
    )

    assert metric["status"] == "conflict"
    assert metric["value"] is None


def test_valuation_score_uses_source_specific_market_thresholds():
    spec = MetricSpec.from_dict(
        {
            "metric_id": "valuation_risk",
            "layer": "ALL",
            "applicable_tickers": ["*"],
            "definition": "valuation",
            "unit": "multiple",
            "period_type": "point_in_time",
            "preferred_source_types": ["market_data"],
            "accepted_source_types": ["market_data"],
            "validator": {"min": 0.0, "max": 1000.0},
            "scoring_usage": "valuation_score",
            "required_for_layer_score": False,
            "thresholds_by_metric": {
                "forward_pe": {
                    "direction": "negative",
                    "thresholds": {"plus2": 15.0, "plus1": 25.0, "minus1": 45.0, "minus2": 70.0},
                }
            },
        }
    )
    indicator_config = {
        "weight": 1.0,
        "direction": "negative",
        "thresholds": {"plus2": 0.10, "plus1": 0.25, "minus1": 0.65, "minus2": 0.85},
    }
    row = score_indicator(
        "valuation_risk",
        {
            "value": 20.0,
            "unit": "multiple",
            "period": "2026-05-01",
            "period_type": "point_in_time",
            "source_type": "market_data",
            "source_id": "fixture",
            "metadata": {"valuation_source_metric": "forward_pe"},
        },
        indicator_config,
        metric_spec=spec,
    )

    assert row["score"] == 1
