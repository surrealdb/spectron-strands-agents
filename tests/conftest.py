"""Shared test fixtures.

FakeSpectron stands in for the real ``surrealdb.Spectron`` client. It records
every call and returns canned responses, so the tools can be tested without a
network connection or a configured Spectron endpoint.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any

import pytest


@dataclass
class Call:
    method: str
    args: tuple
    kwargs: dict


@dataclass
class FakeSpectron:
    calls: list[Call] = field(default_factory=list)

    def _record(self, method: str, *args: Any, **kwargs: Any) -> None:
        self.calls.append(Call(method, args, kwargs))

    def last(self, method: str) -> Call:
        for call in reversed(self.calls):
            if call.method == method:
                return call
        raise AssertionError(f"{method} was never called")

    # Methods mirroring the Spectron client surface used by the tools.
    def remember(self, text: str, **kwargs: Any) -> None:
        self._record("remember", text, **kwargs)

    def recall(self, query: str, **kwargs: Any) -> Any:
        self._record("recall", query, **kwargs)
        return SimpleNamespace(
            hits=[
                SimpleNamespace(score=0.91, text="Alice is the CTO."),
                SimpleNamespace(score=0.42, text="Alice joined in 2021."),
            ]
        )

    def query_context(self, query: str, **kwargs: Any) -> Any:
        self._record("query_context", query, **kwargs)
        return SimpleNamespace(text="Working set: Alice, role changes, org chart.")

    def reflect(self, **kwargs: Any) -> Any:
        self._record("reflect", **kwargs)
        return SimpleNamespace(summary="Merged 3 facts, inferred 1 relationship.")

    def forget(self, query: str, **kwargs: Any) -> Any:
        self._record("forget", query, **kwargs)
        return SimpleNamespace(message="Removed 2 memories.")

    def upload(self, content: str, **kwargs: Any) -> Any:
        self._record("upload", content, **kwargs)
        return SimpleNamespace(status="Uploaded 1 document.")

    def inspect(self, **kwargs: Any) -> Any:
        self._record("inspect", **kwargs)
        return SimpleNamespace(text="2 rows.")


@pytest.fixture
def fake_client() -> FakeSpectron:
    return FakeSpectron()
