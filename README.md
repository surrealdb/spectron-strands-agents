# spectron-strand-agents

Spectron agent memory as tools for the [Strands Agents](https://strandsagents.com) SDK.

[Spectron](https://surrealdb.com/platform/spectron) is SurrealDB's provenance-first, tri-temporal memory and knowledge layer for AI agents. This package exposes Spectron's memory operations as Strands tools, so any Strands agent can store and retrieve long-term memory with a single line of setup:

```python
from strands import Agent
from spectron_strands import spectron_tools

agent = Agent(tools=spectron_tools())

agent("Remember that we signed a contract with Meditech Solutions for 1.2M GBP.")
print(agent("What is the value of the Meditech Solutions contract?"))
```

## Installation

```bash
pip install spectron-strand-agents
```

```bash
pip install "spectron-strand-agents[bedrock]"
```

Requires Python 3.10 or newer.

## Configuration

The tools need a Spectron client. Provide the connection details as environment variables:

```bash
export SPECTRON_ENDPOINT="https://api.spectron.example"
export SPECTRON_API_KEY="your-bearer-token"
export SPECTRON_CONTEXT="acme-prod"
```

With those set, `spectron_tools()` builds the client for you. You can also pass the values directly, or hand in a client you already have:

```python
from surrealdb import Spectron
from spectron_strands import spectron_tools

# From explicit arguments.
tools = spectron_tools(
    endpoint="https://api.spectron.example",
    api_key="your-bearer-token",
    context="acme-prod",
)

# Or reuse an existing client.
client = Spectron(context="acme-prod", endpoint="...", api_key="...")
tools = spectron_tools(client=client)
```

## Tools

`spectron_tools()` returns seven tools by default, one per Spectron operation:

| Tool | Purpose |
| --- | --- |
| `spectron_remember` | Store a fact or observation for later recall. |
| `spectron_recall` | Search memory and return the most relevant stored information. |
| `spectron_context` | Assemble a working-memory context block for a query. |
| `spectron_reflect` | Run a synthesis pass that consolidates and connects memories. |
| `spectron_forget` | Delete memories that match a query. |
| `spectron_upload` | Ingest a document so its contents become recallable. |
| `spectron_inspect` | Browse the substrate as queryable data for debugging or audit. |

Choose a subset with `include` or `exclude`:

```python
# Only the everyday read/write pair.
tools = spectron_tools(include=["remember", "recall"])

# Everything except deletion and inspection.
tools = spectron_tools(exclude=["forget", "inspect"])
```

## Scopes

Spectron scopes isolate memory by principal, tenant or session. A scope is a path
string such as `"org/acme/user/alice"`, or a list of paths. Set a default scope for
all tools, and let the agent override it per call when needed:

```python
tools = spectron_tools(scope="org/acme/user/alice")
```

Every tool also accepts a `scope` argument, so a multi-user agent can direct a
single memory operation at a specific principal.

## How it works

Each tool is a thin wrapper over one method on the synchronous `surrealdb.Spectron`
client. Because that client is synchronous, the tools call it directly. There is no
background event loop or async shim to manage.

Spectron is in early preview. The `remember`, `recall` and `context` tools follow the
documented client signatures. The `reflect`, `forget`, `upload` and `inspect` tools
cover operations whose keyword arguments are still settling. If a method name or
argument differs in the version of `surrealdb` you have installed, the fix is a single
call inside the matching factory in
[`src/spectron_strands/tools.py`](src/spectron_strands/tools.py).

## Examples

Runnable examples live in [`examples/`](examples). They use Amazon Bedrock, which is
Strands' default model provider. See [`examples/README.md`](examples/README.md) for
what each one shows and how to run it.

## Roadmap

- Async tools built on `AsyncSpectron`.
- Streaming `chat` and the grouped resources (`sessions`, `entities`, and others).

## License

Apache License 2.0. See [LICENSE](LICENSE).
