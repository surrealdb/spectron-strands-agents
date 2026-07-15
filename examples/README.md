# Examples

These scripts show `spectron-strands-agents` in use with a real Strands agent. They use
Amazon Bedrock, the default Strands model provider.

## Setup

Install the package with the Bedrock extra:

```bash
pip install "spectron-strands-agents[bedrock]"
```

Point the tools at your Spectron instance:

```bash
export SPECTRON_ENDPOINT="https://api.spectron.example"
export SPECTRON_API_KEY="your-bearer-token"
export SPECTRON_CONTEXT="acme-prod"
```

Configure AWS credentials so Bedrock can serve the model (for example with `aws configure`, or by exporting `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`). To use a different provider, swap the model on the `Agent` as described in the [Strands model providers guide](https://strandsagents.com).

## Scripts

| Script | What it shows |
| --- | --- |
| `quickstart.py` | Store a fact in one turn, recall it in the next. |
| `scoped_memory.py` | Isolate two users' memory with scope paths. |
| `document_memory.py` | Upload a document, then answer questions from it. |
| `reflect_and_context.py` | Consolidate memory with reflect, then read a working-context block. |

Run any script directly:

```bash
python examples/quickstart.py
```
