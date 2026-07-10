"""Consolidate memory with reflect, then read it back as working context.

The agent stores several related facts, runs a reflection pass so Spectron can
merge them and infer relationships, and then pulls a working-context block for a
task. This shows the difference between recall (ranked hits) and context (an
assembled working set).

Prerequisites and setup match examples/quickstart.py.

Run:
    python examples/reflect_and_context.py
"""

from strands import Agent

from spectron_strands import spectron_tools


def main() -> None:
    agent = Agent(tools=spectron_tools(scope="org/acme/project/atlas"))

    agent("Remember that project Atlas ships on 2026-09-01.")
    agent("Remember that Priya leads project Atlas.")
    agent("Remember that Atlas depends on the billing service migration.")

    agent("Reflect over what you know so the facts are consolidated.")

    print(agent("Give me the current working context for planning project Atlas."))


if __name__ == "__main__":
    main()
