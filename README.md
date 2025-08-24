# langchain-parallel-web

LangChain tool and toolkit for Parallel Web search. It exposes a tool that performs web research and returns ranked, compressed excerpts from multiple sources, plus a toolkit to easily wire it into agents.

## Installation

```bash
pip install -U langchain-parallel-web
```

Set your Parallel API key:

```bash
export PARALLEL_API_KEY="your-api-key"
```

You can also pass the key directly to the classes shown below.

## Tool: Parallel Web Search

`ParallelWebTool` exposes the Parallel Web search as a LangChain tool.

```python
from langchain_parallel_web.tools import ParallelWebTool

# Option 1: rely on PARALLEL_API_KEY in env
tool = ParallelWebTool()

# Option 2: pass the key explicitly
# tool = ParallelWebTool(parallel_api_key="your-api-key")

result_json = tool.invoke({
    "objective": "Find when the UN was founded; prefer official sources.",
    "search_queries": [
        "United Nations founding year",
        "When was the UN founded official site"
    ],
})
print(result_json)
```

### Configuration
You can control search behavior via `ParallelWebSearchConfig`.

```python
from langchain_parallel_web.parallel_web_wrapper import ParallelWebSearchConfig
from langchain_parallel_web.tools import ParallelWebTool

config = ParallelWebSearchConfig(
    max_results=10,          # up to 40
    processor="base",        # or "pro"
    max_chars_per_result=1500
)

tool = ParallelWebTool(config=config)
```

## Toolkit: Agent Integration

`ParallelWebToolkit` returns a ready-to-use list of tools for agent setups.

```python
from langchain_parallel_web.toolkits import ParallelWebToolkit

# Pass the key explicitly for the toolkit
toolkit = ParallelWebToolkit(parallel_api_key="your-api-key")

tools = toolkit.get_tools()

# Use `tools` with your LangChain agent or runnable graph
```

## Direct API Wrapper

For lower-level control, call the wrapper directly.

```python
from langchain_parallel_web.parallel_web_wrapper import (
    ParallelWebAPIWrapper,
    ParallelWebSearchInput,
)

wrapper = ParallelWebAPIWrapper()  # uses PARALLEL_API_KEY from env
# or: wrapper = ParallelWebAPIWrapper(parallel_api_key="your-api-key")

payload = ParallelWebSearchInput(
    objective="Summarize key announcements from OpenAI DevDay 2023.",
    search_queries=["OpenAI DevDay 2023 announcements", "OpenAI DevDay keynote summary"],
)

out = wrapper.search(payload)
print(out.model_dump())
```

Async usage is supported:

```python
import asyncio
from langchain_parallel_web.parallel_web_wrapper import (
    ParallelWebAPIWrapper,
    ParallelWebSearchInput,
)

async def main():
    wrapper = ParallelWebAPIWrapper()
    out = await wrapper.asearch(
        ParallelWebSearchInput(
            objective="Latest SEC filing summary for NVDA.",
            search_queries=["NVIDIA latest 10-Q", "NVDA SEC filing"],
        )
    )
    print(out.model_dump())

asyncio.run(main())
```
