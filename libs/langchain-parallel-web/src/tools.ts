import { CallbackManagerForToolRun } from "@langchain/core/callbacks/manager";
import { StructuredTool, type ToolParams } from "@langchain/core/tools";
import type { RunnableConfig } from "@langchain/core/runnables";
import { getEnvironmentVariable } from "@langchain/core/utils/env";
import { z } from "zod";

export type ParallelWebToolFields = ToolParams & {
  apiKey?: string;
  apiUrl?: string; // default below
  config?: {
    max_results?: number;
    processor?: "base" | "pro";
    max_chars_per_result?: number;
  };
};

export class ParallelWebTool extends StructuredTool {
  static lc_name(): string {
    return "ParallelWebTool";
  }

  name = "parallel_web_search";

  description =
    "Research current events; returns ranked, compressed excerpts from multiple sites. Provide a clear objective and a few search queries.";

  // Tip: use z.output<typeof schema> for the parsed shape
  schema = z.object({
    objective: z.string().max(5000, "objective must be <= 5000 characters"),
    search_queries: z.array(z.string()).min(1).max(5, "search_queries must have 1..5 items"),
  });

  protected apiKey?: string;
  protected apiUrl: string;
  protected config: NonNullable<ParallelWebToolFields["config"]>;

  constructor(fields?: ParallelWebToolFields) {
    super(fields);
    this.apiKey = fields?.apiKey ?? getEnvironmentVariable("PARALLEL_API_KEY");
    this.apiUrl = fields?.apiUrl ?? "https://api.parallel.ai/v1beta";
    this.config = {
      max_results: fields?.config?.max_results ?? 10,
      processor: fields?.config?.processor ?? "base",
      max_chars_per_result: fields?.config?.max_chars_per_result ?? 1500,
    };
    if (!this.apiKey) {
      throw new Error('No Parallel API key found. Set "PARALLEL_API_KEY" or pass `apiKey`.');
    }
  }

  protected async _call(
    input: z.output<typeof this.schema>,
    _runManager?: CallbackManagerForToolRun,
    _config?: RunnableConfig<Record<string, any>>
  ): Promise<string> {
    const body = {
      objective: input.objective,
      search_queries: input.search_queries,
      ...this.config,
    };

    const response = await fetch(`${this.apiUrl}/search`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": String(this.apiKey),
      },
      body: JSON.stringify(body),
    });

    let json: any;
    try {
      json = await response.json();
    } catch {
      throw new Error(`Parallel API returned non-JSON (status ${response.status}).`);
    }
    if (!response.ok) {
      const errorMsg = json?.error ?? response.statusText;
      throw new Error(`Parallel API request failed (${response.status}): ${errorMsg}`);
    }
    // Tools should return a string or a ToolMessage (default responseFormat is "content")
    return JSON.stringify(json);
  }
}

