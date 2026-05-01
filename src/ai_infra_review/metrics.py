from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

SOURCE_COMPANY_DISCLOSED = "company_disclosed"
SOURCE_SEC_XBRL = "sec_xbrl"
SOURCE_MARKET_DATA = "market_data"
SOURCE_MEDIA_REPORTED = "media_reported"
SOURCE_ANALYST_ESTIMATED = "analyst_estimated"
SOURCE_MODEL_ESTIMATED = "model_estimated"
SOURCE_MISSING = "missing"

SOURCE_TYPES = {
    SOURCE_COMPANY_DISCLOSED,
    SOURCE_SEC_XBRL,
    SOURCE_MARKET_DATA,
    SOURCE_MEDIA_REPORTED,
    SOURCE_ANALYST_ESTIMATED,
    SOURCE_MODEL_ESTIMATED,
    SOURCE_MISSING,
}

STATUS_MISSING = "missing"
STATUS_CANDIDATE = "candidate"
STATUS_VALIDATED = "validated"
STATUS_CONFIRMED = "confirmed"
STATUS_CONFLICT = "conflict"


class MetricStatus(str, Enum):
    MISSING = STATUS_MISSING
    CANDIDATE = STATUS_CANDIDATE
    VALIDATED = STATUS_VALIDATED
    CONFIRMED = STATUS_CONFIRMED
    CONFLICT = STATUS_CONFLICT


class SourceType(str, Enum):
    COMPANY_DISCLOSED = SOURCE_COMPANY_DISCLOSED
    SEC_XBRL = SOURCE_SEC_XBRL
    MARKET_DATA = SOURCE_MARKET_DATA
    MEDIA_REPORTED = SOURCE_MEDIA_REPORTED
    ANALYST_ESTIMATED = SOURCE_ANALYST_ESTIMATED
    MODEL_ESTIMATED = SOURCE_MODEL_ESTIMATED
    MISSING = SOURCE_MISSING


@dataclass(frozen=True)
class Evidence:
    source_type: str
    source_url: str | None = None
    source_id: str | None = None
    evidence_text: str | None = None
    retrieved_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {key: value for key, value in asdict(self).items() if value is not None}


@dataclass(frozen=True)
class MetricSpec:
    metric_id: str
    layer: str
    applicable_tickers: list[str]
    definition: str
    unit: str
    period_type: str
    preferred_source_types: list[str]
    accepted_source_types: list[str]
    validator: dict[str, Any]
    scoring_usage: str
    required_for_layer_score: bool
    allow_model_estimated_for_layer_scoring: bool = False
    allowed_fallback_metrics: list[str] | None = None
    thresholds_by_metric: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "MetricSpec":
        return cls(
            metric_id=row["metric_id"],
            layer=row.get("layer", "ALL"),
            applicable_tickers=list(row.get("applicable_tickers", ["*"])),
            definition=row.get("definition", ""),
            unit=row.get("unit", ""),
            period_type=row.get("period_type", ""),
            preferred_source_types=list(row.get("preferred_source_types", [])),
            accepted_source_types=list(row.get("accepted_source_types", [])),
            validator=dict(row.get("validator", {})),
            scoring_usage=row.get("scoring_usage", ""),
            required_for_layer_score=bool(row.get("required_for_layer_score", False)),
            allow_model_estimated_for_layer_scoring=bool(row.get("allow_model_estimated_for_layer_scoring", False)),
            allowed_fallback_metrics=list(row.get("allowed_fallback_metrics", [])),
            thresholds_by_metric=dict(row.get("thresholds_by_metric", {})),
        )


@dataclass(frozen=True)
class MetricValue:
    metric_id: str
    value: float | int | str | None
    unit: str | None
    period: str | None
    period_type: str | None
    source_type: str
    status: str
    evidence: list[Evidence]
    confidence: float | None = None
    as_of: str | None = None
    note: str = ""
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "value": self.value,
            "unit": self.unit,
            "period": self.period,
            "period_type": self.period_type,
            "source_type": self.source_type,
            "status": self.status,
            "evidence": [item.to_dict() for item in self.evidence],
            "confidence": self.confidence,
            "as_of": self.as_of,
            "note": self.note,
            "metadata": self.metadata or {},
        }


def metric_catalog_by_id(metric_catalog: dict[str, Any] | None) -> dict[str, MetricSpec]:
    if not metric_catalog:
        return {}
    return {
        row["metric_id"]: MetricSpec.from_dict(row)
        for row in metric_catalog.get("metrics", [])
    }


def clamp(value: float, lower: float = -2.0, upper: float = 2.0) -> float:
    return max(lower, min(upper, value))


def is_missing_metric(metric: dict[str, Any] | None) -> bool:
    if not metric:
        return True
    return (
        metric.get("source_type") == SOURCE_MISSING
        or metric.get("status") == STATUS_MISSING
        or metric.get("value") is None
    )


def _coerce_source_type(source_type: str | SourceType | None) -> str:
    value = source_type.value if isinstance(source_type, SourceType) else source_type
    return value if value in SOURCE_TYPES else SOURCE_MISSING


def _coerce_status(status: str | MetricStatus | None, source_type: str, value: Any) -> str:
    if isinstance(status, MetricStatus):
        return status.value
    if status in {item.value for item in MetricStatus}:
        return str(status)
    if source_type == SOURCE_MISSING or value is None:
        return STATUS_MISSING
    if source_type == SOURCE_MODEL_ESTIMATED:
        return STATUS_VALIDATED
    return STATUS_CANDIDATE


def _coerce_evidence(raw: dict[str, Any], source_type: str) -> list[Evidence]:
    evidence_rows = raw.get("evidence") or []
    evidence: list[Evidence] = []
    for item in evidence_rows:
        if isinstance(item, Evidence):
            evidence.append(item)
        elif isinstance(item, dict):
            evidence.append(
                Evidence(
                    source_type=_coerce_source_type(item.get("source_type", source_type)),
                    source_url=item.get("source_url"),
                    source_id=item.get("source_id"),
                    evidence_text=item.get("evidence_text"),
                    retrieved_at=item.get("retrieved_at"),
                )
            )

    if not evidence and any(raw.get(key) for key in ("source_url", "source_id", "evidence_text")):
        evidence.append(
            Evidence(
                source_type=source_type,
                source_url=raw.get("source_url"),
                source_id=raw.get("source_id"),
                evidence_text=raw.get("evidence_text"),
                retrieved_at=raw.get("retrieved_at"),
            )
        )
    return evidence


def coerce_metric_value(
    metric_id: str,
    raw: dict[str, Any] | MetricValue | None,
    spec: MetricSpec | None = None,
) -> MetricValue:
    if isinstance(raw, MetricValue):
        return raw
    raw = raw or {}
    source_type = _coerce_source_type(raw.get("source_type"))
    value = raw.get("value")
    status = _coerce_status(raw.get("status"), source_type, value)
    return MetricValue(
        metric_id=raw.get("metric_id", metric_id),
        value=value,
        unit=raw.get("unit", spec.unit if spec else None),
        period=raw.get("period", raw.get("as_of")),
        period_type=raw.get("period_type", spec.period_type if spec else None),
        source_type=source_type,
        status=status,
        evidence=_coerce_evidence(raw, source_type),
        confidence=raw.get("confidence"),
        as_of=raw.get("as_of"),
        note=raw.get("note", ""),
        metadata=dict(raw.get("metadata", {})),
    )


def _has_source_identifier(metric: MetricValue) -> bool:
    return any(item.source_url or item.source_id for item in metric.evidence)


def _has_required_evidence_text(metric: MetricValue) -> bool:
    if metric.source_type not in {SOURCE_COMPANY_DISCLOSED, SOURCE_SEC_XBRL}:
        return True
    return any(item.evidence_text for item in metric.evidence)


def _passes_range(metric: MetricValue, spec: MetricSpec) -> bool:
    if metric.value is None:
        return False
    try:
        numeric = float(metric.value)
    except (TypeError, ValueError):
        return False
    validator = spec.validator
    if "min" in validator and numeric < float(validator["min"]):
        return False
    if "max" in validator and numeric > float(validator["max"]):
        return False
    return True


def validate_metric_value(
    metric_id: str,
    raw: dict[str, Any] | MetricValue | None,
    spec: MetricSpec | None = None,
) -> dict[str, Any]:
    if raw and isinstance(raw, dict) and raw.get("candidates"):
        return validate_metric_candidates(metric_id, raw["candidates"], spec)

    metric = coerce_metric_value(metric_id, raw, spec)
    if metric.status == STATUS_CONFLICT:
        return metric.to_dict()
    if spec is None:
        return metric.to_dict()
    if metric.value is None or metric.source_type == SOURCE_MISSING:
        return MetricValue(
            metric_id=metric.metric_id,
            value=None,
            unit=metric.unit,
            period=metric.period,
            period_type=metric.period_type,
            source_type=SOURCE_MISSING,
            status=STATUS_MISSING,
            evidence=metric.evidence,
            confidence=metric.confidence,
            as_of=metric.as_of,
            note=metric.note or "missing",
            metadata=metric.metadata,
        ).to_dict()

    checks_pass = (
        bool(metric.unit)
        and bool(metric.period)
        and bool(metric.period_type)
        and metric.source_type in set(spec.accepted_source_types)
        and _has_source_identifier(metric)
        and _has_required_evidence_text(metric)
        and _passes_range(metric, spec)
    )
    if not checks_pass:
        return MetricValue(
            metric_id=metric.metric_id,
            value=metric.value,
            unit=metric.unit,
            period=metric.period,
            period_type=metric.period_type,
            source_type=metric.source_type,
            status=STATUS_CANDIDATE,
            evidence=metric.evidence,
            confidence=metric.confidence,
            as_of=metric.as_of,
            note=metric.note or "candidate metric failed confirmation checks",
            metadata=metric.metadata,
        ).to_dict()

    status = STATUS_VALIDATED if metric.source_type == SOURCE_MODEL_ESTIMATED else STATUS_CONFIRMED
    return MetricValue(
        metric_id=metric.metric_id,
        value=metric.value,
        unit=metric.unit,
        period=metric.period,
        period_type=metric.period_type,
        source_type=metric.source_type,
        status=status,
        evidence=metric.evidence,
        confidence=metric.confidence,
        as_of=metric.as_of,
        note=metric.note,
        metadata=metric.metadata,
    ).to_dict()


def validate_metric_candidates(
    metric_id: str,
    candidates: list[dict[str, Any] | MetricValue],
    spec: MetricSpec | None = None,
) -> dict[str, Any]:
    validated = [validate_metric_value(metric_id, item, spec) for item in candidates]
    usable = [row for row in validated if row["status"] in {STATUS_CONFIRMED, STATUS_VALIDATED}]
    numeric_values = {round(float(row["value"]), 8) for row in usable if row.get("value") is not None}
    if len(numeric_values) > 1:
        evidence = []
        for row in validated:
            evidence.extend(row.get("evidence", []))
        first = validated[0] if validated else {}
        return {
            "metric_id": metric_id,
            "value": None,
            "unit": first.get("unit", spec.unit if spec else None),
            "period": first.get("period"),
            "period_type": first.get("period_type", spec.period_type if spec else None),
            "source_type": SOURCE_MISSING,
            "status": STATUS_CONFLICT,
            "evidence": evidence,
            "confidence": 0.0,
            "as_of": first.get("as_of"),
            "note": "conflicting metric candidates",
            "candidates": validated,
        }
    return usable[0] if usable else (validated[0] if validated else validate_metric_value(metric_id, None, spec))


def is_usable_for_layer_scoring(metric: dict[str, Any], spec: MetricSpec | None = None) -> bool:
    if metric.get("status") == STATUS_CONFIRMED:
        return True
    if (
        spec
        and metric.get("status") == STATUS_VALIDATED
        and metric.get("source_type") == SOURCE_MODEL_ESTIMATED
        and spec.allow_model_estimated_for_layer_scoring
    ):
        return True
    return False


def normalize_metric_point(metric: dict[str, Any] | None, note: str = "missing") -> dict[str, Any]:
    if is_missing_metric(metric):
        return {
            "value": None,
            "source_type": SOURCE_MISSING,
            "as_of": (metric or {}).get("as_of"),
            "note": (metric or {}).get("note", note),
        }

    source_type = metric.get("source_type")
    if source_type not in SOURCE_TYPES:
        raise ValueError(f"Unsupported source_type: {source_type}")
    return metric


def score_from_thresholds(value: float, direction: str, thresholds: dict[str, float]) -> int:
    plus2 = float(thresholds["plus2"])
    plus1 = float(thresholds["plus1"])
    minus1 = float(thresholds["minus1"])
    minus2 = float(thresholds["minus2"])

    if direction == "negative":
        if value <= plus2:
            return 2
        if value <= plus1:
            return 1
        if value >= minus2:
            return -2
        if value >= minus1:
            return -1
        return 0

    if value >= plus2:
        return 2
    if value >= plus1:
        return 1
    if value <= minus2:
        return -2
    if value <= minus1:
        return -1
    return 0


def weighted_score(rows: list[dict[str, Any]]) -> float:
    rows = [row for row in rows if row.get("score") is not None]
    total_weight = sum(float(row.get("weight", 0.0)) for row in rows)
    if total_weight <= 0:
        return 0.0
    score = sum(float(row["score"]) * float(row.get("weight", 0.0)) for row in rows) / total_weight
    return round(clamp(score), 4)
