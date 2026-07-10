"""Tests for the Spectron tool wrappers."""

from __future__ import annotations

import pytest

from spectron_strands import TOOL_NAMES, spectron_tools


def _by_name(tools):
    return {t.tool_name: t for t in tools}


def test_returns_all_seven_tools(fake_client):
    tools = spectron_tools(client=fake_client)
    assert len(tools) == len(TOOL_NAMES) == 7


def test_every_tool_has_a_usable_spec(fake_client):
    for t in spectron_tools(client=fake_client):
        spec = t.tool_spec
        assert spec["name"]
        assert spec["description"].strip()
        assert "inputSchema" in spec


def test_remember_routes_to_client_with_scope(fake_client):
    tools = _by_name(spectron_tools(client=fake_client, scope="org/acme/user/alice"))
    result = tools["spectron_remember"]("Alice is the CTO.")
    assert "Alice is the CTO." in result
    call = fake_client.last("remember")
    assert call.args[0] == "Alice is the CTO."
    assert call.kwargs["scope"] == "org/acme/user/alice"


def test_per_call_scope_overrides_default(fake_client):
    tools = _by_name(spectron_tools(client=fake_client, scope="default/scope"))
    tools["spectron_remember"]("note", scope="override/scope")
    assert fake_client.last("remember").kwargs["scope"] == "override/scope"


def test_scope_omitted_when_unset(fake_client):
    tools = _by_name(spectron_tools(client=fake_client))
    tools["spectron_remember"]("note")
    assert "scope" not in fake_client.last("remember").kwargs


def test_memory_category_passed_only_when_given(fake_client):
    tools = _by_name(spectron_tools(client=fake_client))
    tools["spectron_remember"]("note", memory_category="context")
    assert fake_client.last("remember").kwargs["memory_category"] == "context"

    tools["spectron_remember"]("note2")
    assert "memory_category" not in fake_client.last("remember").kwargs


def test_recall_formats_hits_with_scores(fake_client):
    tools = _by_name(spectron_tools(client=fake_client))
    out = tools["spectron_recall"]("Who is the CTO?", k=5)
    assert "1. (score 0.910) Alice is the CTO." in out
    assert "2. (score 0.420) Alice joined in 2021." in out
    call = fake_client.last("recall")
    assert call.kwargs["k"] == 5
    assert call.kwargs["mode"] == "hybrid"


def test_recall_handles_empty_results(fake_client):
    fake_client.recall = lambda query, **kw: type("R", (), {"hits": []})()
    tools = _by_name(spectron_tools(client=fake_client))
    assert tools["spectron_recall"]("anything") == "No relevant memories found."


def test_context_returns_block_text(fake_client):
    tools = _by_name(spectron_tools(client=fake_client))
    out = tools["spectron_context"]("current task")
    assert out == "Working set: Alice, role changes, org chart."


def test_reflect_forget_upload_inspect_summaries(fake_client):
    tools = _by_name(spectron_tools(client=fake_client))
    assert "Merged 3 facts" in tools["spectron_reflect"]()
    assert "Removed 2 memories." == tools["spectron_forget"]("old data")
    assert "Uploaded 1 document." == tools["spectron_upload"]("some text", name="notes")
    assert "2 rows." == tools["spectron_inspect"]()

    assert fake_client.last("forget").kwargs["hard"] is False
    assert fake_client.last("upload").kwargs["name"] == "notes"


def test_include_filters_selection(fake_client):
    names = {t.tool_name for t in spectron_tools(client=fake_client, include=["remember", "recall"])}
    assert names == {"spectron_remember", "spectron_recall"}


def test_exclude_filters_selection(fake_client):
    tools = spectron_tools(client=fake_client, exclude=["upload", "inspect", "forget", "reflect"])
    assert len(tools) == 3


def test_unknown_tool_name_raises(fake_client):
    with pytest.raises(ValueError, match="Unknown Spectron tool"):
        spectron_tools(client=fake_client, include=["teleport"])


def test_client_and_kwargs_are_mutually_exclusive(fake_client):
    with pytest.raises(ValueError, match="not both"):
        spectron_tools(client=fake_client, endpoint="https://x")
