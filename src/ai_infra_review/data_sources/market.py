from __future__ import annotations

from datetime import date
import json
import os
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from ai_infra_review.metrics import (
    SOURCE_MARKET_DATA,
    SOURCE_MISSING,
    STATUS_CONFIRMED,
    STATUS_MISSING,
    metric_catalog_by_id,
    validate_metric_value,
)

from .mock import load_mock_metric_snapshot

MARKET_METRIC_IDS = [
    "price",
    "market_cap",
    "trailing_pe",
    "forward_pe",
    "ev_to_ebitda",
    "price_to_sales",
    "beta",
    "volatility",
]

MARKET_UNITS = {
    "price": "usd",
    "market_cap": "usd",
    "trailing_pe": "multiple",
    "forward_pe": "multiple",
    "ev_to_ebitda": "multiple",
    "price_to_sales": "multiple",
    "beta": "ratio",
    "volatility": "ratio",
}


def _missing_canonical_metric(metric_id: str, note: str, *, as_of: str | None = None) -> dict[str, Any]:
    return {
        "metric_id": metric_id,
        "value": None,
        "unit": MARKET_UNITS.get(metric_id),
        "period": as_of or _today(),
        "period_type": "point_in_time",
        "source_type": SOURCE_MISSING,
        "status": STATUS_MISSING,
        "evidence": [],
        "confidence": 0.0,
        "as_of": as_of or _today(),
        "note": note,
        "metadata": {},
    }


def _today() -> str:
    return date.today().isoformat()


def _redact_url(url: str | None) -> str | None:
    if not url:
        return None
    parts = urlsplit(url)
    query = urlencode(
        [
            (key, "REDACTED" if key.lower() == "apikey" else value)
            for key, value in parse_qsl(parts.query, keep_blank_values=True)
        ]
    )
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


def _metric(
    metric_id: str,
    value: Any,
    *,
    provider: str,
    ticker: str,
    source_url: str | None,
    note: str,
    as_of: str | None = None,
) -> dict[str, Any]:
    present = value not in (None, "")
    return {
        "metric_id": metric_id,
        "value": float(value) if present else None,
        "unit": MARKET_UNITS[metric_id],
        "period": as_of or _today(),
        "period_type": "point_in_time",
        "source_type": SOURCE_MARKET_DATA if present else SOURCE_MISSING,
        "status": STATUS_CONFIRMED if present else STATUS_MISSING,
        "confidence": 0.85 if present else 0.0,
        "as_of": as_of or _today(),
        "note": note if present else f"{note} unavailable.",
        "evidence": [
            {
                "source_type": SOURCE_MARKET_DATA if present else SOURCE_MISSING,
                "source_url": _redact_url(source_url),
                "source_id": f"{provider}:{ticker}:{metric_id}",
                "evidence_text": f"{provider} returned {metric_id} directly for {ticker}." if present else None,
            }
        ],
    }


def _set_market_metric_as_of(metric: dict[str, Any], as_of: str | None) -> dict[str, Any]:
    if not as_of:
        return metric
    metric["as_of"] = as_of
    metric["period"] = as_of
    return metric


def build_valuation_metric(
    ticker: str,
    market_row: dict[str, Any] | None,
    metric_catalog: dict[str, Any],
    *,
    as_of: str | None = None,
) -> dict[str, Any]:
    specs = metric_catalog_by_id(metric_catalog)
    valuation_spec = specs.get("valuation_risk")
    if not market_row or not valuation_spec:
        return _missing_canonical_metric("valuation_risk", "No market row available for valuation.", as_of=as_of)

    priority = ["forward_pe"] + list(valuation_spec.allowed_fallback_metrics or [])
    for metric_id in dict.fromkeys(priority):
        raw = market_row.get(metric_id)
        if not raw:
            continue
        candidate = validate_metric_value(
            metric_id,
            _set_market_metric_as_of(dict(raw), as_of),
            specs.get(metric_id),
        )
        if candidate.get("status") != STATUS_CONFIRMED:
            continue
        if metric_id != "forward_pe" and metric_id not in set(valuation_spec.allowed_fallback_metrics or []):
            continue
        return {
            **candidate,
            "metric_id": "valuation_risk",
            "unit": valuation_spec.unit,
            "period_type": valuation_spec.period_type,
            "note": f"Valuation score uses {metric_id} from market data.",
            "metadata": {"valuation_source_metric": metric_id},
        }

    return {
        **_missing_canonical_metric(
            "valuation_risk",
            "No confirmed valuation metric available; forward_pe missing and no allowed fallback confirmed.",
            as_of=as_of,
        ),
        "unit": valuation_spec.unit,
        "period_type": valuation_spec.period_type,
    }


def _missing_market_row(ticker: str, note: str, *, provider: str = "missing") -> dict[str, Any]:
    row = {"ticker": ticker, "provider": provider}
    for metric_id in MARKET_METRIC_IDS:
        row[metric_id] = _metric(metric_id, None, provider=provider, ticker=ticker, source_url=None, note=note)
    return row


def _mock_market_snapshot(tickers: list[str]) -> dict[str, dict[str, Any]]:
    mock_companies = {company["ticker"]: company for company in load_mock_metric_snapshot()["companies"]}
    rows = {}
    for ticker in tickers:
        if ticker in mock_companies:
            rows[ticker] = _missing_market_row(ticker, "Mock mode has no market data", provider="mock")
        else:
            rows[ticker] = _missing_market_row(ticker, "Ticker not present in mock snapshot", provider="mock")
    return rows


def _read_json(url: str, *, opener=urlopen, headers: dict[str, str] | None = None) -> Any:
    request = Request(url, headers=headers or {})
    with opener(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _first_number(*values: Any) -> float | None:
    for value in values:
        if value in (None, ""):
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _first_row(payload: Any) -> dict[str, Any]:
    if isinstance(payload, list) and payload and isinstance(payload[0], dict):
        return payload[0]
    if isinstance(payload, dict):
        return payload
    return {}


def _safe_read_json(url: str, *, opener=urlopen) -> Any:
    try:
        return _read_json(url, opener=opener)
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError):
        return {}


def _fetch_fmp(tickers: list[str], api_key: str, *, opener=urlopen) -> dict[str, dict[str, Any]]:
    symbol_param = ",".join(tickers)
    quote_url = "https://financialmodelingprep.com/stable/batch-quote?" + urlencode(
        {"symbols": symbol_param, "apikey": api_key}
    )
    quote_payload = _read_json(quote_url, opener=opener)
    by_symbol = {item.get("symbol"): item for item in quote_payload if isinstance(item, dict)}
    rows = {}

    for ticker in tickers:
        item = by_symbol.get(ticker)
        if not item:
            rows[ticker] = _missing_market_row(ticker, "Provider returned no quote row", provider="fmp")
            continue

        ratios_url = "https://financialmodelingprep.com/stable/ratios-ttm?" + urlencode(
            {"symbol": ticker, "apikey": api_key}
        )
        key_metrics_url = "https://financialmodelingprep.com/stable/key-metrics-ttm?" + urlencode(
            {"symbol": ticker, "apikey": api_key}
        )
        profile_url = "https://financialmodelingprep.com/stable/profile?" + urlencode(
            {"symbol": ticker, "apikey": api_key}
        )
        ratios = _first_row(_safe_read_json(ratios_url, opener=opener))
        key_metrics = _first_row(_safe_read_json(key_metrics_url, opener=opener))
        profile = _first_row(_safe_read_json(profile_url, opener=opener))

        forward_pe = _first_number(item.get("forwardPE"), item.get("forwardPe"), key_metrics.get("forwardPE"))
        trailing_pe = _first_number(
            item.get("pe"),
            item.get("peRatio"),
            ratios.get("priceToEarningsRatioTTM"),
            ratios.get("priceEarningsRatioTTM"),
            ratios.get("peRatioTTM"),
            key_metrics.get("peRatioTTM"),
        )
        price_to_sales = _first_number(
            ratios.get("priceToSalesRatioTTM"),
            ratios.get("priceToSalesTTM"),
            key_metrics.get("priceToSalesRatioTTM"),
        )
        ev_to_ebitda = _first_number(
            ratios.get("enterpriseValueMultipleTTM"),
            ratios.get("evToEBITDATTM"),
            key_metrics.get("enterpriseValueOverEBITDATTM"),
            key_metrics.get("evToEBITDATTM"),
        )
        beta = _first_number(item.get("beta"), profile.get("beta"))

        rows[ticker] = {
            "ticker": ticker,
            "provider": "fmp",
            "price": _metric("price", item.get("price"), provider="fmp", ticker=ticker, source_url=quote_url, note="FMP quote price"),
            "market_cap": _metric("market_cap", item.get("marketCap"), provider="fmp", ticker=ticker, source_url=quote_url, note="FMP quote market cap"),
            "forward_pe": _metric("forward_pe", forward_pe, provider="fmp", ticker=ticker, source_url=quote_url, note="FMP forward PE"),
            "trailing_pe": _metric("trailing_pe", trailing_pe, provider="fmp", ticker=ticker, source_url=ratios_url, note="FMP trailing PE"),
            "ev_to_ebitda": _metric("ev_to_ebitda", ev_to_ebitda, provider="fmp", ticker=ticker, source_url=key_metrics_url, note="FMP EV/EBITDA"),
            "price_to_sales": _metric("price_to_sales", price_to_sales, provider="fmp", ticker=ticker, source_url=ratios_url, note="FMP price to sales"),
            "beta": _metric("beta", beta, provider="fmp", ticker=ticker, source_url=profile_url, note="FMP beta"),
            "volatility": _metric("volatility", None, provider="fmp", ticker=ticker, source_url=None, note="FMP volatility"),
        }
    return rows


def _fetch_alphavantage(tickers: list[str], api_key: str, *, opener=urlopen) -> dict[str, dict[str, Any]]:
    rows = {}
    for ticker in tickers:
        url = "https://www.alphavantage.co/query?" + urlencode(
            {"function": "GLOBAL_QUOTE", "symbol": ticker, "apikey": api_key}
        )
        payload = _read_json(url, opener=opener)
        quote = payload.get("Global Quote", {})
        price = quote.get("05. price")
        row = _missing_market_row(ticker, "Alpha Vantage quote endpoint does not return this metric", provider="alphavantage")
        row["price"] = _metric("price", price, provider="alphavantage", ticker=ticker, source_url=url, note="Alpha Vantage global quote price")
        rows[ticker] = row
    return rows


def fetch_market_snapshot(
    tickers: list[str],
    *,
    env: Mapping[str, str] | None = None,
    opener=urlopen,
) -> dict[str, dict[str, Any]]:
    runtime_env = env or os.environ
    provider = runtime_env.get("MARKET_DATA_PROVIDER", "mock").lower()
    api_key = runtime_env.get("MARKET_DATA_API_KEY")
    cleaned_tickers = [ticker for ticker in tickers if ticker and ticker != "CASH"]

    if not api_key or provider == "mock":
        return _mock_market_snapshot(cleaned_tickers)
    try:
        if provider == "fmp":
            return _fetch_fmp(cleaned_tickers, api_key, opener=opener)
        if provider in {"alphavantage", "alpha_vantage"}:
            return _fetch_alphavantage(cleaned_tickers, api_key, opener=opener)
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {
            ticker: _missing_market_row(ticker, f"{provider} request failed: {exc}", provider=provider)
            for ticker in cleaned_tickers
        }

    raise ValueError(f"Unsupported MARKET_DATA_PROVIDER: {provider}")
