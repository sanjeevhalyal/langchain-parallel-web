from __future__ import annotations

import json
from typing import Any

import pytest

from langchain_parallel_web.parallel_web_wrapper import (
    ParallelWebSearchInput,
    ParallelWebSearchOutput,
)
from langchain_parallel_web.tools import ParallelWebTool


class _DummyWrapper:
    """Stub for `ParallelWebAPIWrapper` avoiding network calls."""

    def __init__(self, response_payload: dict[str, Any]):
        self._response_payload = response_payload
        self.last_input: ParallelWebSearchInput | None = None

    def search(self, input_payload: ParallelWebSearchInput) -> ParallelWebSearchOutput:  # type: ignore[override]
        self.last_input = input_payload
        return ParallelWebSearchOutput(**self._response_payload)

    async def asearch(  # type: ignore[override]
        self, input_payload: ParallelWebSearchInput
    ) -> ParallelWebSearchOutput:
        self.last_input = input_payload
        return ParallelWebSearchOutput(**self._response_payload)


def test_parallel_web_tool_run_returns_json_with_expected_fields() -> None:
    # Arrange: stub wrapper returns a structured response
    payload = {
        "search_id": "search-123",
        "results": {
            "url": "https://example.com",
            "title": "Example Title",
            "excerpts": ["snippet 1", "snippet 2"],
        },
    }
    dummy_wrapper = _DummyWrapper(payload)

    tool = ParallelWebTool(parallel_api_key="dummy-key")
    # Inject the stub to avoid real HTTP
    tool._api_wrapper = dummy_wrapper  # type: ignore[attr-defined]

    # Act: call the tool's underlying run implementation
    result = tool.invoke(
        input={
            "objective": "Find launch date of the UN",
            "search_queries": ["When was UN founded?"],
        }  # type: ignore[attr-defined]
    )

    # Assert: result is JSON string of the expected shape
    assert isinstance(result, str)
    data = json.loads(result)
    assert data["search_id"] == payload["search_id"]
    assert set(data["results"].keys()) == {"url", "title", "excerpts"}

    # Also validate the input passed into the wrapper
    assert isinstance(dummy_wrapper.last_input, ParallelWebSearchInput)
    assert dummy_wrapper.last_input.objective == "Find launch date of the UN"
    assert dummy_wrapper.last_input.search_queries == ["When was UN founded?"]


@pytest.mark.asyncio
async def test_parallel_web_tool_arun_returns_json_with_expected_fields() -> None:
    # Arrange: async stub wrapper returns a structured response
    payload = {
        "search_id": "search-async-123",
        "results": {
            "url": "https://example.org",
            "title": "Async Example",
            "excerpts": ["async snippet 1", "async snippet 2"],
        },
    }
    dummy_wrapper = _DummyWrapper(payload)

    tool = ParallelWebTool(parallel_api_key="dummy-key")
    # Inject the stub to avoid real HTTP
    tool._api_wrapper = dummy_wrapper  # type: ignore[attr-defined]

    # Act: call the tool's async implementation via ainvoke
    result = await tool.ainvoke(
        input={
            "objective": "Find async test path",
            "search_queries": ["async testing best practices"],
        }  # type: ignore[attr-defined]
    )

    # Assert: result is JSON string of the expected shape
    assert isinstance(result, str)
    data = json.loads(result)
    assert data["search_id"] == payload["search_id"]
    assert set(data["results"].keys()) == {"url", "title", "excerpts"}

    # Validate the input passed into the wrapper
    assert isinstance(dummy_wrapper.last_input, ParallelWebSearchInput)
    assert dummy_wrapper.last_input.objective == "Find async test path"
    assert dummy_wrapper.last_input.search_queries == ["async testing best practices"]
