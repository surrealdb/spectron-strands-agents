"""Quickstart: give a Strands agent memory backed by Spectron.

The agent stores a fact in one turn and recalls it in the next.

Prerequisites:
    pip install "spectron-strands-agents[bedrock]"

    export SPECTRON_ENDPOINT="https://api.spectron.example"
    export SPECTRON_API_KEY="your-bearer-token"
    export SPECTRON_CONTEXT="acme-prod"

Amazon Bedrock is the default Strands model provider, so also configure AWS
credentials (for example with the AWS CLI) before running this.

Run:
    python examples/quickstart.py
"""

from strands import Agent

from spectron_strands import spectron_tools


def main() -> None:
    agent = Agent(tools=spectron_tools())

    agent("Remember that we signed a contract with Meditech Solutions for 1.2M GBP.")

    answer = agent("What is the value of the Meditech Solutions contract?")
    print(answer)


if __name__ == "__main__":
    main()
