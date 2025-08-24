# langchain-parallel-web

LangChain.js tool integration for Parallel’s web research API. It provides a `StructuredTool` that researches current events and returns ranked, compressed excerpts from multiple sites based on your objective and search queries.

## Installation

```bash npm2yarn
npm install langchain-parallel-web @langchain/core
```

This package, along with the main LangChain packages, depends on `@langchain/core`.
If you are using this package with other LangChain packages, ensure they all depend on the same version of `@langchain/core`. One way is to add the following to your project’s `package.json`:

```json
{
  "dependencies": {
    "@langchain/core": "^0.3.0",
    "langchain-parallel-web": "^0.0.1"
  },
  "resolutions": {
    "@langchain/core": "^0.3.0"
  },
  "overrides": {
    "@langchain/core": "^0.3.0"
  },
  "pnpm": {
    "overrides": {
      "@langchain/core": "^0.3.0"
    }
  }
}
```

## Setup

```bash
export PARALLEL_API_KEY=your-api-key
```

Node.js 18+ is required.

## Usage

### Direct invocation

```typescript
import { ParallelWebTool } from "langchain-parallel-web";

const tool = new ParallelWebTool({
  // You can also omit this and rely on PARALLEL_API_KEY env var
  apiKey: process.env.PARALLEL_API_KEY,
  // Optional overrides
  // apiUrl: "https://api.parallel.ai/v1beta",
  // config: { max_results: 10, processor: "base", max_chars_per_result: 1500 },
});

const output = await tool.invoke({
  objective: "Summarize the latest impacts of Hurricane Beryl on air travel.",
  search_queries: [
    "Hurricane Beryl flight cancellations",
    "airlines response Beryl"
  ],
});

// Tool returns a JSON string; parse it as needed
const results = JSON.parse(output);
console.log(results);
```

CommonJS usage:

```javascript
const { ParallelWebTool } = require("langchain-parallel-web");
```

### With agents (conceptual)

`ParallelWebTool` is a LangChain `StructuredTool`, so you can register it with your agent/tool-using chain as you would other tools. Provide clear objectives and a small set of focused queries for best results.

## API

### Class: `ParallelWebTool`

- name: `parallel_web_search`
- description: Research current events; returns ranked, compressed excerpts from multiple sites.

Constructor fields:

- apiKey: string (optional). Defaults to `process.env.PARALLEL_API_KEY`. Required if env var not set.
- apiUrl: string (optional). Defaults to `https://api.parallel.ai/v1beta`.
- config (optional):
  - max_results?: number (default 10)
  - processor?: "base" | "pro" (default "base")
  - max_chars_per_result?: number (default 1500)

Input schema (validated):

- objective: string, up to 5000 characters
- search_queries: string[], between 1 and 5 items

Return value:

- A JSON string of the Parallel API response. Parse with `JSON.parse` to access structured results.

## Development

### Install dependencies

```bash
yarn install
# or: npm install
```

### Build the package

```bash
yarn build
# or: npm run build
```

### Run tests

```bash
yarn test
# or: npm test
```

### Lint & Format

```bash
yarn lint && yarn format
# or: npm run lint && npm run format
```

### Adding new entrypoints

If you add a new file to be exported, either import & re-export it from `src/index.ts`, or add it to the `entrypoints` field in `config` inside `langchain.config.js`, then rebuild.

