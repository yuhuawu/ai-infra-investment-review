from __future__ import annotations

import json
import os
from typing import Any, Mapping
from urllib.request import Request, urlopen

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"


class SECConfigurationError(RuntimeError):
    pass


def _sec_user_agent(env: Mapping[str, str] | None = None) -> str:
    value = (env or os.environ).get("SEC_USER_AGENT")
    if not value:
        raise SECConfigurationError(
            "SEC_USER_AGENT is required for SEC EDGAR requests. "
            "Set it to an app/contact string, for example: 'ai-infra-review contact@example.com'."
        )
    return value


def _get_json(url: str, user_agent: str, opener=urlopen) -> dict[str, Any]:
    request = Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "application/json",
        },
    )
    with opener(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_cik(cik: str | int) -> str:
    return str(cik).strip().lstrip("0").zfill(10)


def fetch_company_ticker_map(*, env: Mapping[str, str] | None = None, opener=urlopen) -> dict[str, str]:
    user_agent = _sec_user_agent(env)
    payload = _get_json(SEC_TICKERS_URL, user_agent, opener=opener)
    return {
        str(record["ticker"]).upper(): normalize_cik(record["cik_str"])
        for record in payload.values()
    }


def cik_for_ticker(ticker: str, *, env: Mapping[str, str] | None = None, opener=urlopen) -> str:
    ticker_map = fetch_company_ticker_map(env=env, opener=opener)
    try:
        return ticker_map[ticker.upper()]
    except KeyError as exc:
        raise KeyError(f"Ticker {ticker!r} was not found in the SEC company ticker map.") from exc


def fetch_recent_filings(
    *,
    ticker: str | None = None,
    cik: str | int | None = None,
    limit: int = 10,
    forms: set[str] | None = None,
    env: Mapping[str, str] | None = None,
    opener=urlopen,
) -> list[dict[str, Any]]:
    if ticker is None and cik is None:
        raise ValueError("Provide either ticker or cik.")

    user_agent = _sec_user_agent(env)
    normalized_cik = normalize_cik(cik) if cik is not None else cik_for_ticker(ticker or "", env=env, opener=opener)
    payload = _get_json(SEC_SUBMISSIONS_URL.format(cik=normalized_cik), user_agent, opener=opener)
    recent = payload.get("filings", {}).get("recent", {})
    accession_numbers = recent.get("accessionNumber", [])
    form_filter = {form.upper() for form in forms} if forms else None

    rows = []
    for index, accession_number in enumerate(accession_numbers):
        form = recent.get("form", [""])[index]
        if form_filter and form.upper() not in form_filter:
            continue
        primary_document = recent.get("primaryDocument", [""])[index]
        accession_compact = accession_number.replace("-", "")
        rows.append(
            {
                "ticker": ticker.upper() if ticker else None,
                "cik": normalized_cik,
                "accession_number": accession_number,
                "filing_date": recent.get("filingDate", [None])[index],
                "report_date": recent.get("reportDate", [None])[index],
                "form": form,
                "primary_document": primary_document,
                "filing_url": (
                    f"https://www.sec.gov/Archives/edgar/data/"
                    f"{int(normalized_cik)}/{accession_compact}/{primary_document}"
                ),
                "source_type": "company_disclosed",
            }
        )
        if len(rows) >= limit:
            break
    return rows


def fetch_company_filings(ticker: str, limit: int = 10) -> list[dict[str, Any]]:
    return fetch_recent_filings(ticker=ticker, limit=limit)
