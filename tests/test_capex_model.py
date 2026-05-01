from ai_infra_review.capex_model import estimate_capex_transmission, estimate_vendor_impact


def test_estimate_vendor_impact_calculates_revenue_profit_and_market_cap():
    impact = estimate_vendor_impact(
        hyperscaler="META",
        capex_increment=10_000_000_000,
        category="accelerators",
        category_share=0.50,
        vendor={
            "ticker": "NVDA",
            "layer": "L2",
            "vendor_share": 0.80,
            "revenue_capture": 0.65,
            "margin": 0.55,
            "tax_rate": 0.15,
            "forward_pe": 30,
            "market_cap": 4_000_000_000_000,
        },
    )

    assert impact["incremental_revenue"] == 2_600_000_000
    assert impact["incremental_ebit"] == 1_430_000_000
    assert impact["incremental_net_income"] == 1_215_500_000
    assert impact["estimated_market_cap_impact"] == 36_465_000_000
    assert impact["estimated_stock_impact_pct"] == 0.009116
    assert impact["source_type"] == "model_estimated"
    assert impact["confidence"] == 0.7


def test_estimate_capex_transmission_outputs_three_scenarios_and_aggregates_tickers():
    config = {
        "default_event": {"hyperscaler": "META", "capex_increment": 1000, "source_type": "media_reported"},
        "depreciation_years": 5,
        "hyperscalers": {"META": {"tax_rate": 0.15, "market_cap": 10000}},
        "category_shares": {"accelerators": 0.5, "networking": 0.5},
        "vendors": {
            "accelerators": [
                {
                    "ticker": "AAA",
                    "layer": "L2",
                    "vendor_share": 0.5,
                    "revenue_capture": 0.5,
                    "margin": 0.5,
                    "tax_rate": 0.2,
                    "forward_pe": 10,
                    "market_cap": 10000,
                }
            ],
            "networking": [
                {
                    "ticker": "AAA",
                    "layer": "L2",
                    "vendor_share": 0.5,
                    "revenue_capture": 0.5,
                    "margin": 0.5,
                    "tax_rate": 0.2,
                    "forward_pe": 10,
                    "market_cap": 10000,
                }
            ],
        },
    }

    result = estimate_capex_transmission(config)

    assert set(result["scenarios"]) == {"conservative", "base", "aggressive"}
    base = result["scenarios"]["base"]
    assert base["buyer_impact"]["source_type"] == "model_estimated"
    assert base["ticker_impacts"][0]["ticker"] == "AAA"
    assert base["ticker_impacts"][0]["incremental_revenue"] == 250
    assert base["ticker_impacts"][0]["source_type"] == "model_estimated"
    assert base["ticker_impacts"][0]["assumptions_used"]
