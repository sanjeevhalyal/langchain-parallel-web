import { CallbackManagerForToolRun } from "@langchain/core/callbacks/manager";
import { StructuredTool, type ToolParams } from "@langchain/core/tools";
import type { RunnableConfig } from "@langchain/core/runnables";
import { z } from "zod";
export type ParallelWebToolFields = ToolParams & {
    apiKey?: string;
    apiUrl?: string;
    config?: {
        max_results?: number;
        processor?: "base" | "pro";
        max_chars_per_result?: number;
    };
};
export declare class ParallelWebTool extends StructuredTool {
    static lc_name(): string;
    name: string;
    description: string;
    schema: z.ZodObject<{
        objective: z.ZodString;
        search_queries: z.ZodArray<z.ZodString, "many">;
    }, "strip", z.ZodTypeAny, {
        objective: string;
        search_queries: string[];
    }, {
        objective: string;
        search_queries: string[];
    }>;
    protected apiKey?: string;
    protected apiUrl: string;
    protected config: NonNullable<ParallelWebToolFields["config"]>;
    constructor(fields?: ParallelWebToolFields);
    protected _call(input: z.output<typeof this.schema>, _runManager?: CallbackManagerForToolRun, _config?: RunnableConfig<Record<string, any>>): Promise<string>;
}
