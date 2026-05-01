import json
from urllib.error import HTTPError

import pytest

from ai_infra_review.data_sources.company_ir import download_document, fetch_investor_relations_updates
from ai_infra_review.data_sources.market import build_valuation_metric, fetch_market_snapshot
from ai_infra_review.data_sources.sec import SECConfigurationError, fetch_recent_filings


class FakeResponse:
    def __init__(self, payload, content_type="application/json"):
        self.payload = payload
        self.headers = {"Content-Type": content_type}

    def read(self):
        if isinstance(self.payload, bytes):
            return self.payload
        if isinstance(self.payload, str):
            return self.payload.encode("utf-8")
        return json.dumps(self.payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_sec_requires_user_agent():
    with pytest.raises(SECConfigurationError, match="SEC_USER_AGENT"):
        fetch_recent_filings(ticker="MSFT", env={})


def test_sec_fetch_recent_filings_by_ticker_uses_mocked_responses():
    def opener(request, timeout=30):
        url = request.full_url
        if url.endswith("/company_tickers.json"):
            return FakeResponse({"0": {"ticker": "MSFT", "cik_str": 789019}})
        assert "CIK0000789019.json" in url
        return FakeResponse(
            {
                "filings": {
                    "recent": {
                        "accessionNumber": ["0000789019-26-000001"],
                        "filingDate": ["2026-04-30"],
                        "reportDate": ["2026-03-31"],
                        "form": ["10-Q"],
                        "primaryDocument": ["msft-20260331.htm"],
                    }
                }
            }
        )

    rows = fetch_recent_filings(ticker="MSFT", env={"SEC_USER_AGENT": "test contact@example.com"}, opener=opener)

    assert rows[0]["cik"] == "0000789019"
    assert rows[0]["form"] == "10-Q"
    assert rows[0]["source_type"] == "company_disclosed"


def test_company_ir_downloads_html_and_marks_unparsed_metric_missing():
    def opener(request, timeout=30):
        return FakeResponse("<html>earnings</html>", "text/html; charset=utf-8")

    document = download_document("https://example.com/earnings", opener=opener)
    rows = fetch_investor_relations_updates(
        "NVDA",
        {"company_ir": {"NVDA": {"ir_pages": ["https://example.com/earnings"], "earnings_release_urls": []}}},
        opener=opener,
    )

    assert document["content_kind"] == "html"
    assert rows[0]["status"] == "downloaded"
    assert rows[0]["parsed_metrics"]["earnings_release_metric"]["source_type"] == "missing"


def test_company_ir_downloads_pdf_without_parsing():
    def opener(request, timeout=30):
        return FakeResponse(b"%PDF-1.7 fake", "application/pdf")

    document = download_document("https://example.com/report.pdf", opener=opener)

    assert document["content_kind"] == "pdf"
    assert document["text"] is None
    assert document["source_type"] == "company_disclosed"


def test_market_falls_back_to_mock_without_api_key():
    rows = fetch_market_snapshot(["NVDA"], env={})

    assert rows["NVDA"]["provider"] == "mock"
    assert rows["NVDA"]["forward_pe"]["source_type"] == "missing"


def test_market_fmp_marks_missing_forward_pe_when_absent():
    def opener(request, timeout=30):
        url = request.full_url
        if "financialmodelingprep.com/stable/batch-quote" in url:
            assert "symbols=NVDA" in url
            return FakeResponse([{"symbol": "NVDA", "price": 100.0, "marketCap": 1000.0}])
        if "financialmodelingprep.com/stable/ratios-ttm" in url:
            return FakeResponse([{"priceEarningsRatioTTM": 32.0, "priceToSalesRatioTTM": 14.0}])
        if "financialmodelingprep.com/stable/key-metrics-ttm" in url:
            return FakeResponse([{"enterpriseValueOverEBITDATTM": 28.0}])
        if "financialmodelingprep.com/stable/profile" in url:
            return FakeResponse([{"beta": 1.4}])
        raise AssertionError(url)

    rows = fetch_market_snapshot(
        ["NVDA"],
        env={"MARKET_DATA_PROVIDER": "fmp", "MARKET_DATA_API_KEY": "secret"},
        opener=opener,
    )

    assert rows["NVDA"]["price"]["value"] == 100.0
    assert rows["NVDA"]["market_cap"]["value"] == 1000.0
    assert rows["NVDA"]["forward_pe"]["source_type"] == "missing"
    assert rows["NVDA"]["trailing_pe"]["value"] == 32.0
    assert rows["NVDA"]["price_to_sales"]["value"] == 14.0
    assert rows["NVDA"]["ev_to_ebitda"]["value"] == 28.0
    assert rows["NVDA"]["beta"]["value"] == 1.4


def test_market_fmp_uses_forward_pe_when_present():
    def opener(request, timeout=30):
        url = request.full_url
        if "financialmodelingprep.com/stable/batch-quote" in url:
            return FakeResponse([{"symbol": "NVDA", "price": 100.0, "marketCap": 1000.0, "forwardPE": 25.0}])
        if "financialmodelingprep.com/stable/ratios-ttm" in url:
            return FakeResponse([{}])
        if "financialmodelingprep.com/stable/key-metrics-ttm" in url:
            return FakeResponse([{}])
        if "financialmodelingprep.com/stable/profile" in url:
            return FakeResponse([{}])
        raise AssertionError(url)

    rows = fetch_market_snapshot(
        ["NVDA"],
        env={"MARKET_DATA_PROVIDER": "fmp", "MARKET_DATA_API_KEY": "secret"},
        opener=opener,
    )

    assert rows["NVDA"]["forward_pe"]["value"] == 25.0
    assert rows["NVDA"]["forward_pe"]["source_type"] == "market_data"


def test_valuation_metric_prefers_forward_pe_and_allows_configured_fallback():
    catalog = {
        "metrics": [
            {"metric_id": "forward_pe", "layer": "ALL", "applicable_tickers": ["*"], "definition": "", "unit": "multiple", "period_type": "point_in_time", "preferred_source_types": ["market_data"], "accepted_source_types": ["market_data"], "validator": {"min": 0.0, "max": 1000.0}, "scoring_usage": "valuation_score", "required_for_layer_score": False},
            {"metric_id": "trailing_pe", "layer": "ALL", "applicable_tickers": ["*"], "definition": "", "unit": "multiple", "period_type": "point_in_time", "preferred_source_types": ["market_data"], "accepted_source_types": ["market_data"], "validator": {"min": 0.0, "max": 1000.0}, "scoring_usage": "valuation_score", "required_for_layer_score": False},
            {"metric_id": "price_to_sales", "layer": "ALL", "applicable_tickers": ["*"], "definition": "", "unit": "multiple", "period_type": "point_in_time", "preferred_source_types": ["market_data"], "accepted_source_types": ["market_data"], "validator": {"min": 0.0, "max": 1000.0}, "scoring_usage": "valuation_score", "required_for_layer_score": False},
            {"metric_id": "valuation_risk", "layer": "ALL", "applicable_tickers": ["*"], "definition": "", "unit": "multiple", "period_type": "point_in_time", "preferred_source_types": ["market_data"], "accepted_source_types": ["market_data"], "validator": {"min": 0.0, "max": 1000.0}, "scoring_usage": "valuation_score", "required_for_layer_score": False, "allowed_fallback_metrics": ["trailing_pe"]},
        ]
    }
    market_row = {
        "forward_pe": {"value": None, "source_type": "missing", "status": "missing", "unit": "multiple", "period": "2026-05-01", "period_type": "point_in_time", "evidence": []},
        "trailing_pe": {"value": 31.0, "source_type": "market_data", "status": "confirmed", "unit": "multiple", "period": "2026-05-01", "period_type": "point_in_time", "evidence": [{"source_type": "market_data", "source_id": "fixture"}]},
        "price_to_sales": {"value": 14.0, "source_type": "market_data", "status": "confirmed", "unit": "multiple", "period": "2026-05-01", "period_type": "point_in_time", "evidence": [{"source_type": "market_data", "source_id": "fixture"}]},
    }

    metric = build_valuation_metric("NVDA", market_row, catalog, as_of="2026-05-01")

    assert metric["status"] == "confirmed"
    assert metric["value"] == 31.0
    assert metric["metadata"]["valuation_source_metric"] == "trailing_pe"


def test_valuation_metric_does_not_use_unconfigured_fallback():
    catalog = {
        "metrics": [
            {"metric_id": "forward_pe", "layer": "ALL", "applicable_tickers": ["*"], "definition": "", "unit": "multiple", "period_type": "point_in_time", "preferred_source_types": ["market_data"], "accepted_source_types": ["market_data"], "validator": {"min": 0.0, "max": 1000.0}, "scoring_usage": "valuation_score", "required_for_layer_score": False},
            {"metric_id": "price_to_sales", "layer": "ALL", "applicable_tickers": ["*"], "definition": "", "unit": "multiple", "period_type": "point_in_time", "preferred_source_types": ["market_data"], "accepted_source_types": ["market_data"], "validator": {"min": 0.0, "max": 1000.0}, "scoring_usage": "valuation_score", "required_for_layer_score": False},
            {"metric_id": "valuation_risk", "layer": "ALL", "applicable_tickers": ["*"], "definition": "", "unit": "multiple", "period_type": "point_in_time", "preferred_source_types": ["market_data"], "accepted_source_types": ["market_data"], "validator": {"min": 0.0, "max": 1000.0}, "scoring_usage": "valuation_score", "required_for_layer_score": False, "allowed_fallback_metrics": []},
        ]
    }
    market_row = {
        "forward_pe": {"value": None, "source_type": "missing", "status": "missing", "unit": "multiple", "period": "2026-05-01", "period_type": "point_in_time", "evidence": []},
        "price_to_sales": {"value": 14.0, "source_type": "market_data", "status": "confirmed", "unit": "multiple", "period": "2026-05-01", "period_type": "point_in_time", "evidence": [{"source_type": "market_data", "source_id": "fixture"}]},
    }

    metric = build_valuation_metric("NVDA", market_row, catalog, as_of="2026-05-01")

    assert metric["status"] == "missing"
    assert metric["value"] is None


def test_market_provider_failure_returns_missing_rows():
    def opener(request, timeout=30):
        raise HTTPError(request.full_url, 403, "Forbidden", hdrs=None, fp=None)

    rows = fetch_market_snapshot(
        ["NVDA"],
        env={"MARKET_DATA_PROVIDER": "fmp", "MARKET_DATA_API_KEY": "secret"},
        opener=opener,
    )

    assert rows["NVDA"]["provider"] == "fmp"
    assert rows["NVDA"]["price"]["source_type"] == "missing"
    assert "403" in rows["NVDA"]["price"]["note"]
