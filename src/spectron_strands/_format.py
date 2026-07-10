"""Helpers that turn Spectron response objects into plain text for the model.

Strands wraps a string return value from a tool into a tool result, so every
tool in this package hands back a readable string. The renderers here are
deliberately defensive: they accept typed Spectron objects (``.hits``,
``.score``, ``.text``) as well as plain dicts, so a small change in the SDK
response shape does not break the tools.
"""

from __future__ import annotations

from typing import Any


def _field(obj: Any, name: str, default: Any = None) -> Any:
    """Read ``name`` from an object attribute or a dict key."""
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _as_hits(response: Any) -> list[Any]:
    """Pull the list of hits out of a recall response of unknown shape."""
    if response is None:
        return []
    if isinstance(response, list):
        return response
    hits = _field(response, "hits")
    if hits is None:
        results = _field(response, "results")
        return list(results) if results else []
    return list(hits)


def format_recall(response: Any) -> str:
    """Render a recall response as a numbered list with relevance scores."""
    hits = _as_hits(response)
    if not hits:
        return "No relevant memories found."

    lines = []
    for index, hit in enumerate(hits, start=1):
        text = _field(hit, "text") or _field(hit, "content") or str(hit)
        score = _field(hit, "score")
        if isinstance(score, (int, float)):
            lines.append(f"{index}. (score {score:.3f}) {text}")
        else:
            lines.append(f"{index}. {text}")
    return "\n".join(lines)


def format_context(block: Any) -> str:
    """Render a working-context block as text."""
    if block is None:
        return "No working context available."
    if isinstance(block, str):
        return block or "No working context available."
    text = _field(block, "text") or _field(block, "context") or _field(block, "content")
    if text:
        return str(text)
    return str(block)


def summarize(result: Any, fallback: str) -> str:
    """Best-effort one-line summary for operations without a rich response."""
    if result is None:
        return fallback
    for name in ("summary", "message", "text", "status"):
        value = _field(result, name)
        if value:
            return str(value)
    return str(result)
