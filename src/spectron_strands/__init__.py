"""Spectron agent memory as tools for the Strands Agents SDK.

Give a Strands agent persistent memory backed by Spectron:

    from strands import Agent
    from spectron_strands import spectron_tools

    agent = Agent(tools=spectron_tools())
    agent("Remember that our launch date is 2026-09-01.")
    print(agent("When do we launch?"))
"""

from __future__ import annotations

from .client import build_client
from .tools import TOOL_NAMES, spectron_tools

__all__ = ["spectron_tools", "build_client", "TOOL_NAMES", "__version__"]

__version__ = "0.1.0"
