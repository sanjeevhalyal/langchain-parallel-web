import { describe, expect, it, beforeEach, afterEach, jest } from "@jest/globals";
import { ParallelWebTool } from "../tools.js";

describe("ParallelWebTool (unit)", () => {
  const ORIGINAL_ENV = { ...process.env } as Record<string, string | undefined>;
  let originalFetch: any;

  beforeEach(() => {
    originalFetch = (global as any).fetch;
    // Ensure we control env within tests
    delete (process.env as any).PARALLEL_API_KEY;
  });

  afterEach(() => {
    (global as any).fetch = originalFetch;
    // Restore environment
    for (const k of Object.keys(process.env)) delete (process.env as any)[k];
    Object.assign(process.env, ORIGINAL_ENV);
  });

  it("throws if no apiKey provided via env or constructor", () => {
    expect(() => new ParallelWebTool()).toThrow(
      'No Parallel API key found. Set "PARALLEL_API_KEY" or pass `apiKey`.'
    );
  });

  it("constructs with provided apiKey and default config", () => {
    expect(() => new ParallelWebTool({ apiKey: "test-key" })).not.toThrow();
  });

  it("validates input schema bounds", () => {
    const tool = new ParallelWebTool({ apiKey: "x" });
    const tooMany = tool.schema.safeParse({
      objective: "o",
      search_queries: ["a", "b", "c", "d", "e", "f"],
    });
    expect(tooMany.success).toBe(false);

    const ok = tool.schema.safeParse({
      objective: "research",
      search_queries: ["one"],
    });
    expect(ok.success).toBe(true);
  });

  it("calls the API with headers, body, and returns JSON string", async () => {
    const jsonPayload = { foo: "bar" };
    const fetchMock = jest.fn<typeof fetch>();
    fetchMock.mockResolvedValue({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => jsonPayload,
    } as unknown as Response);
    (global as any).fetch = fetchMock;

    const tool = new ParallelWebTool({ apiKey: "test-key", apiUrl: "https://example.com" });
    const input = { objective: "test", search_queries: ["x", "y"] } as const;
    const res = await tool.invoke(input);

    expect(typeof res).toBe("string");
    expect(res).toBe(JSON.stringify(jsonPayload));

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("https://example.com/search");
    expect((init!.headers as Record<string, string>)["x-api-key"]).toBe("test-key");
    expect((init!.headers as Record<string, string>)["content-type"]).toBe("application/json");
    const bodyParsed = JSON.parse(String(init!.body));
    expect(bodyParsed.objective).toBe("test");
    expect(bodyParsed.search_queries).toEqual(["x", "y"]);
    expect(bodyParsed).toHaveProperty("max_results");
    expect(bodyParsed).toHaveProperty("processor");
    expect(bodyParsed).toHaveProperty("max_chars_per_result");
  });

  it("throws a helpful error when API returns non-JSON", async () => {
    const fetchMock = jest.fn<typeof fetch>();
    fetchMock.mockResolvedValue({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => {
        throw new Error("invalid json");
      },
    } as unknown as Response);
    (global as any).fetch = fetchMock;

    const tool = new ParallelWebTool({ apiKey: "test-key" });
    await expect(
      tool.invoke({ objective: "o", search_queries: ["a"] })
    ).rejects.toThrow("Parallel API returned non-JSON (status 200).");
  });

  it("throws with API error details when response not ok", async () => {
    const fetchMock = jest.fn<typeof fetch>();
    fetchMock.mockResolvedValue({
      ok: false,
      status: 400,
      statusText: "Bad Request",
      json: async () => ({ error: "Boom" }),
    } as unknown as Response);
    (global as any).fetch = fetchMock;

    const tool = new ParallelWebTool({ apiKey: "test-key" });
    await expect(
      tool.invoke({ objective: "o", search_queries: ["a"] })
    ).rejects.toThrow("Parallel API request failed (400): Boom");
  });
});
