import json
from typing import Any, Dict, List, Literal

import aiohttp
import requests
from langchain_core.utils import get_from_dict_or_env
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    computed_field,
    model_validator,
)

PARALLEL_API_URL = "https://api.parallel.ai/v1beta"


class ParallelWebSearchInput(BaseModel):
    objective: str = Field(
        max_length=5000,
        description="""Natural-language description of what the web research goal is.
        Include any source or freshness guidance.""",
        examples=["I want to know when the UN was founded. Prefer UN’s websites."],
    )
    search_queries: List[str] = Field(
        max_length=5,
        default_factory=List,
        description="search queries to guide the search",
        examples=[["Founding year UN”, “Year of founding United Nations"]],
    )


class ParallelWebSearchConfig(BaseModel):
    max_results: int = Field(max_length=40, default=10)
    processor: Literal["base", "pro"] = Field(default="base")
    max_chars_per_result: int = Field(min_length=100, max_length=30000, default=1500)


class _ParallelWebSearchExcerptResults(BaseModel):
    url: str
    title: str
    excerpts: List[str]


class ParallelWebSearchOutput(BaseModel):
    search_id: str
    results: _ParallelWebSearchExcerptResults


class ParallelWebAPIWrapper(BaseModel):
    base_url: str = Field(default=PARALLEL_API_URL)
    parallel_api_key: SecretStr

    config: ParallelWebSearchConfig = Field(default_factory=ParallelWebSearchConfig)

    model_config = ConfigDict(
        extra="forbid",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict) -> Any:
        """Validate that api key and endpoint exists in environment."""
        parallel_api_key = get_from_dict_or_env(
            values, "parallel_api_key", "PARALLEL_API_KEY"
        )
        values["parallel_api_key"] = parallel_api_key

        return values

    @computed_field
    @property
    def search_url(self) -> str:
        return self.base_url + "/search"

    def search(self, input_payload: ParallelWebSearchInput) -> ParallelWebSearchOutput:
        response = requests.post(
            self.search_url,
            data={**input_payload.model_dump(), **self.config.model_dump()},
            headers={
                "x-api-key": f"${self.parallel_api_key}",
                "Content-Type": "application/json",
            },
        )

        response.raise_for_status()

        data = json.loads(response.text)
        return ParallelWebSearchOutput(**data)

    async def _acall(
        self, session: aiohttp.ClientSession, input_payload: ParallelWebSearchInput
    ) -> str:
        data = ({**input_payload.model_dump(), **self.config.model_dump()},)
        headers = {
            "x-api-key": f"${self.parallel_api_key}",
            "Content-Type": "application/json",
        }

        async with session.post(
            self.search_url, data=data, headers=headers
        ) as response:
            response.raise_for_status()
            return await response.text()

    async def asearch(
        self, input_payload: ParallelWebSearchInput
    ) -> ParallelWebSearchOutput:
        async with aiohttp.ClientSession() as session:
            response_text = await self._acall(
                session=session, input_payload=input_payload
            )
        data = json.loads(response_text)
        return ParallelWebSearchOutput(**data)
