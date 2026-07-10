"""Spectron memory operations exposed as Strands tools.

``spectron_tools()`` returns a list of Strands tools that an agent can call to
store and retrieve memory in Spectron. Each tool wraps one method on the
synchronous ``surrealdb.Spectron`` client. Because that client is synchronous,
the tools call it directly and do not need an event-loop shim.

The wrappers are intentionally thin. ``remember``, ``recall`` and ``context``
follow the documented Spectron client signatures. ``reflect``, ``forget``,
``upload`` and ``inspect`` cover operations whose keyword arguments are still
settling during Spectron's early preview; if a method name or argument differs
in the version of ``surrealdb`` you have installed, adjust the single call
inside the matching factory below.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable

from strands import tool

from .client import build_client
from ._format import format_context, format_recall, summarize

# Scope may be a single path or a list of paths, e.g. "org/acme/user/alice".
Scope = str | list[str] | None

# The full set of tool names, in a stable order.
TOOL_NAMES = ("remember", "recall", "context", "reflect", "forget", "upload", "inspect")


def _resolve_scope(call_scope: Scope, default_scope: Scope) -> Scope:
    """Prefer a scope passed on the call, otherwise use the configured default."""
    return call_scope if call_scope is not None else default_scope


def _with_scope(scope: Scope, **kwargs: Any) -> dict[str, Any]:
    """Build a kwargs dict, adding ``scope`` only when it is set."""
    if scope is not None:
        kwargs["scope"] = scope
    return {key: value for key, value in kwargs.items() if value is not None}


def _make_remember(client: Any, default_scope: Scope) -> Any:
    @tool
    def spectron_remember(
        text: str,
        scope: str | None = None,
        memory_category: str | None = None,
    ) -> str:
        """Store a fact or observation in Spectron memory for later recall.

        Use this whenever the user shares information that should be remembered
        across turns or sessions, such as preferences, decisions or facts.

        Args:
            text: The information to remember, written in natural language.
            scope: Optional scope path, for example "org/acme/user/alice". Falls
                back to the scope configured on the tools.
            memory_category: Optional category such as "context" or "knowledge".
        """
        resolved = _resolve_scope(scope, default_scope)
        client.remember(text, **_with_scope(resolved, memory_category=memory_category))
        return f"Remembered: {text}"

    return spectron_remember


def _make_recall(client: Any, default_scope: Scope) -> Any:
    @tool
    def spectron_recall(
        query: str,
        k: int = 10,
        mode: str = "hybrid",
        scope: str | None = None,
    ) -> str:
        """Search Spectron memory and return the most relevant stored information.

        Use this before answering when the question may depend on something
        remembered earlier.

        Args:
            query: A natural language description of what to look for.
            k: Maximum number of results to return.
            mode: Retrieval mode, for example "hybrid", "vector" or "text".
            scope: Optional scope path to search within. Falls back to the scope
                configured on the tools.
        """
        resolved = _resolve_scope(scope, default_scope)
        response = client.recall(query, **_with_scope(resolved, k=k, mode=mode))
        return format_recall(response)

    return spectron_recall


def _make_context(client: Any, default_scope: Scope) -> Any:
    @tool
    def spectron_context(
        query: str,
        k: int = 10,
        scope: str | None = None,
    ) -> str:
        """Assemble the current working-memory context for a query.

        Returns a ready-to-use context block drawn from active topics and the
        relevant working set, rather than a ranked list of individual hits.

        Args:
            query: A natural language description of the current task or question.
            k: Maximum number of items to fold into the context.
            scope: Optional scope path. Falls back to the scope configured on the
                tools.
        """
        resolved = _resolve_scope(scope, default_scope)
        block = client.query_context(query, **_with_scope(resolved, k=k))
        return format_context(block)

    return spectron_context


def _make_reflect(client: Any, default_scope: Scope) -> Any:
    @tool
    def spectron_reflect(scope: str | None = None) -> str:
        """Run a synthesis pass so Spectron consolidates and connects memories.

        Use this after storing a batch of related facts to let Spectron infer
        relationships and merge fragmented knowledge.

        Args:
            scope: Optional scope path to reflect over. Falls back to the scope
                configured on the tools.
        """
        resolved = _resolve_scope(scope, default_scope)
        # Early-preview signature; adjust the kwargs here if your surrealdb differs.
        result = client.reflect(**_with_scope(resolved))
        return summarize(result, "Reflection pass complete.")

    return spectron_reflect


def _make_forget(client: Any, default_scope: Scope) -> Any:
    @tool
    def spectron_forget(
        query: str,
        hard: bool = False,
        scope: str | None = None,
    ) -> str:
        """Delete memories that match a query from Spectron.

        Args:
            query: A natural language description of what to forget.
            hard: When true, remove permanently rather than marking as forgotten.
            scope: Optional scope path. Falls back to the scope configured on the
                tools.
        """
        resolved = _resolve_scope(scope, default_scope)
        # Early-preview signature; adjust the kwargs here if your surrealdb differs.
        result = client.forget(query, **_with_scope(resolved, hard=hard))
        return summarize(result, f"Forgot memories matching: {query}")

    return spectron_forget


def _make_upload(client: Any, default_scope: Scope) -> Any:
    @tool
    def spectron_upload(
        content: str,
        name: str | None = None,
        scope: str | None = None,
    ) -> str:
        """Ingest a document into Spectron so its contents become recallable.

        Args:
            content: The document text to ingest.
            name: Optional name or title for the document.
            scope: Optional scope path. Falls back to the scope configured on the
                tools.
        """
        resolved = _resolve_scope(scope, default_scope)
        # Early-preview signature; adjust the call here if your surrealdb differs.
        result = client.upload(content, **_with_scope(resolved, name=name))
        return summarize(result, f"Uploaded document{f' {name!r}' if name else ''}.")

    return spectron_upload


def _make_inspect(client: Any, default_scope: Scope) -> Any:
    @tool
    def spectron_inspect(
        query: str | None = None,
        scope: str | None = None,
    ) -> str:
        """Browse the Spectron substrate as queryable data for debugging or audit.

        Args:
            query: Optional filter describing what to inspect.
            scope: Optional scope path. Falls back to the scope configured on the
                tools.
        """
        resolved = _resolve_scope(scope, default_scope)
        # Early-preview signature; adjust the call here if your surrealdb differs.
        result = client.inspect(**_with_scope(resolved, query=query))
        return summarize(result, "No matching records.")

    return spectron_inspect


_FACTORIES: dict[str, Callable[[Any, Scope], Any]] = {
    "remember": _make_remember,
    "recall": _make_recall,
    "context": _make_context,
    "reflect": _make_reflect,
    "forget": _make_forget,
    "upload": _make_upload,
    "inspect": _make_inspect,
}


def _select(include: Iterable[str] | None, exclude: Iterable[str] | None) -> list[str]:
    """Resolve the ordered list of tool names to build."""
    names = list(include) if include is not None else list(TOOL_NAMES)
    unknown = [name for name in names if name not in _FACTORIES]
    if unknown:
        raise ValueError(
            f"Unknown Spectron tool name(s): {', '.join(unknown)}. "
            f"Valid names are: {', '.join(TOOL_NAMES)}."
        )
    if exclude:
        excluded = set(exclude)
        names = [name for name in names if name not in excluded]
    return names


def spectron_tools(
    client: Any | None = None,
    *,
    scope: Scope = None,
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
    **client_kwargs: Any,
) -> list[Any]:
    """Build Spectron memory tools ready to hand to a Strands ``Agent``.

    Args:
        client: An existing ``surrealdb.Spectron`` client. When omitted, one is
            built with ``build_client(**client_kwargs)`` from arguments or the
            environment.
        scope: A default scope (a path string or list of path strings) applied to
            every tool. Each tool also accepts a per-call ``scope`` that overrides
            this default.
        include: Tool names to build. Defaults to all seven. See ``TOOL_NAMES``.
        exclude: Tool names to leave out of the selection.
        **client_kwargs: Passed to ``build_client`` when ``client`` is not given
            (context, endpoint, api_key, timeout, max_retries).

    Returns:
        A list of Strands tools, one per selected Spectron operation.
    """
    if client is None:
        client = build_client(**client_kwargs)
    elif client_kwargs:
        raise ValueError("Pass either an existing client or client_kwargs, not both.")

    names = _select(include, exclude)
    return [_FACTORIES[name](client, scope) for name in names]
