import json
from typing import Any, Dict

import pytest

from langchain_parallel_web.parallel_web_wrapper import (
    ParallelWebAPIWrapper,
    ParallelWebSearchInput,
)


class DummyResponse:
    def __init__(self, status_code: int, payload: Dict[str, Any]):
        self.status_code = status_code
        self.text = json.dumps(payload)
        self._raised = False

    def raise_for_status(self) -> None:  # pragma: no cover - trivial
        # mimic requests.Response.raise_for_status for 2xx
        if not (200 <= self.status_code < 300):
            self._raised = True
            raise Exception("HTTP error")


def test_validate_environment_uses_env(monkeypatch: pytest.MonkeyPatch) -> None:
    # Ensure the model validator reads from env when no key is provided
    monkeypatch.setenv("PARALLEL_API_KEY", "env-secret-key")

    wrapper = ParallelWebAPIWrapper.model_validate({})

    # pydantic's SecretStr stores the value retrievable via get_secret_value
    assert wrapper.parallel_api_key.get_secret_value() == "env-secret-key"


def test_search_url_property_default() -> None:
    wrapper = ParallelWebAPIWrapper.model_validate({"parallel_api_key": "abc"})
    assert wrapper.search_url.endswith("/search")
    assert wrapper.search_url == f"{wrapper.base_url}/search"


def test_search_posts_and_parses_response(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange wrapper and input
    wrapper = ParallelWebAPIWrapper.model_validate({"parallel_api_key": "abc"})
    input_payload = ParallelWebSearchInput(
        objective="Find UN founding year",
        search_queries=["Founding year UN", "Year of founding United Nations"],
    )

    captured: Dict[str, Any] = {}

    def fake_post(url: str, data: Dict[str, Any], headers: Dict[str, str]):
        captured["url"] = url
        captured["data"] = data
        captured["headers"] = headers
        payload = {
            "search_id": "sid-123",
            "results": {
                "url": "https://www.un.org/en/about-us/un-charter",
                "title": "UN Charter",
                "excerpts": [
                    "The United Nations was founded in 1945 after World War II.",
                ],
            },
        }
        return DummyResponse(200, payload)

    monkeypatch.setattr(
        "langchain_parallel_web.parallel_web_wrapper.requests.post", fake_post
    )

    # Act
    out = wrapper.search(input_payload)

    # Assert request construction
    assert captured["url"] == wrapper.search_url
    # data should be a merge of input and config dumps
    expected_data = {
        **input_payload.model_dump(),
        **wrapper.config.model_dump(),
    }
    assert captured["data"] == expected_data

    # Basic header sanity: required keys present
    assert captured["headers"]["Content-Type"] == "application/json"
    assert "x-api-key" in captured["headers"]

    # Assert response mapping into model
    assert out.search_id == "sid-123"
    assert out.results.url.startswith("https://www.un.org/")
    assert out.results.title == "UN Charter"
    assert any("founded" in e.lower() for e in out.results.excerpts)


@pytest.mark.asyncio
async def test_asearch_uses_acall_and_parses(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange wrapper and input
    wrapper = ParallelWebAPIWrapper.model_validate({"parallel_api_key": "abc"})
    input_payload = ParallelWebSearchInput(
        objective="Find async UN founding year",
        search_queries=["UN founding year"],
    )

    captured: Dict[str, Any] = {}

    async def fake_acall(self: ParallelWebAPIWrapper, session, input_payload):  # type: ignore[no-untyped-def]
        captured["session_type"] = type(session).__name__
        captured["input_payload"] = input_payload
        payload = {
            "search_id": "sid-async-123",
            "results": {
                "url": "https://www.un.org/",
                "title": "UN Home",
                "excerpts": ["Founded in 1945."],
            },
        }
        return json.dumps(payload)

    monkeypatch.setattr(ParallelWebAPIWrapper, "_acall", fake_acall, raising=True)

    # Act
    out = await wrapper.asearch(input_payload)

    # Assert response mapping into model
    assert out.search_id == "sid-async-123"
    assert out.results.url == "https://www.un.org/"
    assert out.results.title == "UN Home"
    assert out.results.excerpts == ["Founded in 1945."]

    # And ensure _acall received the same logical input
    assert captured["input_payload"].model_dump() == input_payload.model_dump()
