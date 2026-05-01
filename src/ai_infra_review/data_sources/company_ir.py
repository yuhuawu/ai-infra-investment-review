from __future__ import annotations

from datetime import date
from typing import Any
from urllib.request import Request, urlopen


def missing_metric(note: str, *, as_of: str | None = None) -> dict[str, Any]:
    return {
        "value": None,
        "source_type": "missing",
        "as_of": as_of or date.today().isoformat(),
        "note": note,
    }


def download_document(url: str, *, opener=urlopen, timeout: int = 30) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "ai-infra-investment-review/0.1"})
    with opener(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "application/octet-stream")
        raw = response.read()

    lower_content_type = content_type.lower()
    if "pdf" in lower_content_type or url.lower().endswith(".pdf"):
        return {
            "url": url,
            "content_type": content_type,
            "content_kind": "pdf",
            "bytes": raw,
            "text": None,
            "source_type": "company_disclosed",
        }

    if "html" in lower_content_type:
        kind = "html"
    elif "text" in lower_content_type:
        kind = "text"
    else:
        kind = "binary"

    text = raw.decode("utf-8", errors="replace") if kind in {"html", "text"} else None
    return {
        "url": url,
        "content_type": content_type,
        "content_kind": kind,
        "bytes": raw if kind == "binary" else None,
        "text": text,
        "source_type": "company_disclosed",
    }


def configured_urls_for_ticker(data_sources_config: dict[str, Any], ticker: str) -> list[str]:
    company_config = data_sources_config.get("company_ir", {}).get(ticker.upper(), {})
    return [
        *company_config.get("ir_pages", []),
        *company_config.get("earnings_release_urls", []),
    ]


def fetch_investor_relations_updates(
    ticker: str,
    data_sources_config: dict[str, Any],
    *,
    opener=urlopen,
) -> list[dict[str, Any]]:
    urls = configured_urls_for_ticker(data_sources_config, ticker)
    if not urls:
        return [
            {
                "ticker": ticker.upper(),
                "url": None,
                "status": "missing",
                "metric": missing_metric(f"No IR URLs configured for {ticker.upper()}."),
            }
        ]

    rows = []
    for url in urls:
        try:
            document = download_document(url, opener=opener)
            rows.append(
                {
                    "ticker": ticker.upper(),
                    "url": url,
                    "status": "downloaded",
                    "document": {
                        "url": document["url"],
                        "content_type": document["content_type"],
                        "content_kind": document["content_kind"],
                        "source_type": document["source_type"],
                        "content_length": len(document.get("bytes") or (document.get("text") or "").encode("utf-8")),
                        "text_preview": (document.get("text") or "")[:500] if document.get("text") else None,
                    },
                    "parsed_metrics": {
                        "earnings_release_metric": missing_metric(
                            "IR document downloaded but no robust parser is implemented yet."
                        )
                    },
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "ticker": ticker.upper(),
                    "url": url,
                    "status": "error",
                    "metric": missing_metric(f"Failed to download IR document: {exc}"),
                }
            )
    return rows
