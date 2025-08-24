"""ParallelWeb tools."""

from typing import Any, List, Optional, Type

from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_parallel_web.parallel_web_wrapper import (
    ParallelWebAPIWrapper,
    ParallelWebSearchConfig,
    ParallelWebSearchInput,
)


class ParallelWebTool(BaseTool):  # type: ignore[override]
    name: str = "Parallel Web Search"
    """The name that is passed to the model when performing tool calling."""
    description: str = """Tool to research and get ranked, compressed excerpts for 
    questions about current events from several websites. Input should be main 
    objective of the web research and additional guidance 
    """

    args_schema: Type[BaseModel] = ParallelWebSearchInput  # type: ignore[override]
    """The schema that is passed to the model when performing tool calling."""

    parallel_api_key: Optional[str]

    config: Optional[ParallelWebSearchConfig] = Field(
        default_factory=ParallelWebSearchConfig
    )

    _api_wrapper: ParallelWebAPIWrapper

    def __init__(self, **kwargs: Any) -> None:
        # Create api_wrapper with tavily_api_key if provided
        if "parallel_api_key" in kwargs:
            kwargs["api_wrapper"] = ParallelWebAPIWrapper(
                parallel_api_key=kwargs["parallel_api_key"]
            )

        super().__init__(**kwargs)

    def _run(
        self,
        objective: str,
        search_queries: List[str],
        *,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        return self._api_wrapper.search(
            ParallelWebSearchInput(objective=objective, search_queries=search_queries)
        ).model_dump_json()

    async def _arun(
        self,
        objective: str,
        search_queries: List[str],
        *,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        result = await self._api_wrapper.asearch(
            ParallelWebSearchInput(objective=objective, search_queries=search_queries)
        )
        return result.model_dump_json()
