"""Helpers for reading schema.org JSON-LD blocks that the crawler parsed."""

from __future__ import annotations

from typing import Any

from crawler.models import PageData


def schema_nodes(page: PageData) -> list[dict[str, Any]]:
    """Every schema.org node on the page, including those inside an @graph list."""
    nodes: list[dict[str, Any]] = []
    for block in page.structured_data:
        graph = block.get("@graph")
        nodes += [n for n in graph if isinstance(n, dict)] if isinstance(graph, list) else [block]
    return nodes


def node_types(node: dict[str, Any]) -> set[str]:
    """The node's @type values. @type may be a string or a list of strings."""
    raw = node.get("@type", [])
    return {raw} if isinstance(raw, str) else {t for t in raw if isinstance(t, str)}
