"""Construction of the Spectron client used by the tools.

The Spectron client lives in the ``surrealdb`` package, v3 alpha or later
(``pip install "surrealdb>=3.0.0a1"``).
It is imported lazily so that importing ``spectron_strands`` never requires a
configured environment, and so a missing dependency produces a clear message
rather than an import error at package load time.
"""

from __future__ import annotations

import os
from typing import Any

# Environment variables read by build_client when an argument is not supplied.
ENV_CONTEXT = "SPECTRON_CONTEXT"
ENV_ENDPOINT = "SPECTRON_ENDPOINT"
ENV_API_KEY = "SPECTRON_API_KEY"


def build_client(
    *,
    context: str | None = None,
    endpoint: str | None = None,
    api_key: str | None = None,
    timeout: float = 30.0,
    max_retries: int = 3,
) -> Any:
    """Build a synchronous Spectron client from arguments or the environment.

    Any argument left as ``None`` falls back to its environment variable:
    ``SPECTRON_CONTEXT``, ``SPECTRON_ENDPOINT`` and ``SPECTRON_API_KEY``.

    Args:
        context: Spectron context id, for example ``"acme-prod"``.
        endpoint: Spectron host URL, for example ``"https://api.spectron.example"``.
        api_key: Bearer token used to authenticate requests.
        timeout: Per-request timeout in seconds.
        max_retries: Retry attempts for idempotent operations.

    Returns:
        A ``surrealdb.Spectron`` instance.

    Raises:
        ImportError: If the ``surrealdb`` package is not installed.
        ValueError: If context, endpoint or api_key cannot be resolved.
    """
    context = context or os.getenv(ENV_CONTEXT)
    endpoint = endpoint or os.getenv(ENV_ENDPOINT)
    api_key = api_key or os.getenv(ENV_API_KEY)

    missing = [
        name
        for name, value in (
            (ENV_CONTEXT, context),
            (ENV_ENDPOINT, endpoint),
            (ENV_API_KEY, api_key),
        )
        if not value
    ]
    if missing:
        raise ValueError(
            "Spectron client configuration is incomplete. Provide it as arguments "
            "to build_client / spectron_tools, or set these environment variables: "
            + ", ".join(missing)
        )

    try:
        from surrealdb import Spectron
    except ImportError as exc:  # pragma: no cover - exercised only without surrealdb
        raise ImportError(
            "The 'surrealdb' package is required for the Spectron client. "
            "Spectron ships in the v3 alpha; install it with: "
            'pip install "surrealdb>=3.0.0a1"'
        ) from exc

    return Spectron(
        context=context,
        endpoint=endpoint,
        api_key=api_key,
        timeout=timeout,
        max_retries=max_retries,
    )
