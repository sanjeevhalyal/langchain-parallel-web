import { StructuredTool } from "@langchain/core/tools";
import { getEnvironmentVariable } from "@langchain/core/utils/env";
import { z } from "zod";
export class ParallelWebTool extends StructuredTool {
    static lc_name() {
        return "ParallelWebTool";
    }
    constructor(fields) {
        super(fields);
        this.name = "parallel_web_search";
        this.description = "Research current events; returns ranked, compressed excerpts from multiple sites. Provide a clear objective and a few search queries.";
        // Tip: use z.output<typeof schema> for the parsed shape
        this.schema = z.object({
            objective: z.string().max(5000, "objective must be <= 5000 characters"),
            search_queries: z.array(z.string()).min(1).max(5, "search_queries must have 1..5 items"),
        });
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
    async _call(input, _runManager, _config) {
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
        let json;
        try {
            json = await response.json();
        }
        catch {
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
