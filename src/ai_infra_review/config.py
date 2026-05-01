from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:
    yaml = None


@dataclass(frozen=True)
class ReviewConfig:
    layers: list[dict[str, Any]]
    indicators: dict[str, Any]
    metric_catalog: dict[str, Any]
    portfolio: dict[str, Any]
    capex_transmission: dict[str, Any]
    data_sources: dict[str, Any]


def _load_yaml(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text) or {}
    return json.loads(text)


def load_review_config(config_dir: Path | str) -> ReviewConfig:
    base = Path(config_dir)
    config = ReviewConfig(
        layers=_load_yaml(base / "layers.yaml").get("layers", []),
        indicators=_load_yaml(base / "indicators.yaml"),
        metric_catalog=_load_yaml(base / "metric_catalog.yaml"),
        portfolio=_load_yaml(base / "portfolio.yaml").get("portfolio", {}),
        capex_transmission=_load_yaml(base / "capex_transmission.yaml"),
        data_sources=_load_yaml(base / "data_sources.yaml") if (base / "data_sources.yaml").exists() else {},
    )
    validate_review_config(config)
    return config


def validate_review_config(config: ReviewConfig) -> None:
    if not config.layers:
        raise ValueError("layers.yaml must define at least one layer")
    if "layers" not in config.indicators:
        raise ValueError("indicators.yaml must define layer indicator settings")
    if "metrics" not in config.metric_catalog:
        raise ValueError("metric_catalog.yaml must define metrics")
    if "holdings" not in config.portfolio:
        raise ValueError("portfolio.yaml must define holdings")
    if config.portfolio.get("allow_auto_trade") is not False:
        raise ValueError("portfolio.yaml must explicitly disable automatic trading")
    if config.portfolio.get("allow_broker_connection") is not False:
        raise ValueError("portfolio.yaml must explicitly disable broker connections")
