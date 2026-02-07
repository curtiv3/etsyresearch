from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = Path("config/default.yaml")
DOMAINS_CONFIG_PATH = Path("config/domains.yaml")


@dataclass
class QueryExpansionConfig:
    max_followups: int
    max_queue_size: int


@dataclass
class DedupeConfig:
    similarity_threshold: float


@dataclass
class SearchConfig:
    searx_url: str
    timeout_s: int
    max_retries: int
    user_agent: str


@dataclass
class Config:
    search: SearchConfig
    dedupe: DedupeConfig
    expansion: QueryExpansionConfig
    domain_filters: dict[str, Any]


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_config(path: Path | None = None) -> Config:
    config_path = path or DEFAULT_CONFIG_PATH
    raw = load_yaml(config_path)
    search = SearchConfig(
        searx_url=str(raw["search"]["searx_url"]),
        timeout_s=int(raw["search"]["timeout_s"]),
        max_retries=int(raw["search"]["max_retries"]),
        user_agent=str(raw["search"]["user_agent"]),
    )
    dedupe = DedupeConfig(similarity_threshold=float(raw["dedupe"]["similarity_threshold"]))
    expansion = QueryExpansionConfig(
        max_followups=int(raw["expansion"]["max_followups"]),
        max_queue_size=int(raw["expansion"]["max_queue_size"]),
    )
    domain_filters = raw.get("domain_filters", {})
    return Config(search=search, dedupe=dedupe, expansion=expansion, domain_filters=domain_filters)


def load_domains(path: Path | None = None) -> dict[str, Any]:
    config_path = path or DOMAINS_CONFIG_PATH
    return load_yaml(config_path)
