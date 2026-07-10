"""Per-user memory with scopes.

A scope isolates one principal's memory from another's. Here two agents share a
Spectron context but write and read under different scope paths, so a fact stored
for Alice does not surface when acting for Bob.

Prerequisites and setup match examples/quickstart.py.

Run:
    python examples/scoped_memory.py
"""

from strands import Agent

from spectron_strands import spectron_tools


def agent_for(user: str) -> Agent:
    return Agent(tools=spectron_tools(scope=f"org/acme/user/{user}"))


def main() -> None:
    alice = agent_for("alice")
    bob = agent_for("bob")

    alice("Remember that my preferred contact method is email.")
    bob("Remember that my preferred contact method is phone.")

    print("Alice:", alice("How do I prefer to be contacted?"))
    print("Bob:", bob("How do I prefer to be contacted?"))


if __name__ == "__main__":
    main()
