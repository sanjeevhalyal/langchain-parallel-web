"""ParallelWeb toolkits."""

from typing import List

from langchain_core.tools import BaseTool, BaseToolkit
from pydantic import ConfigDict, Field

from langchain_parallel_web.tools import ParallelWebTool


class ParallelWebToolkit(BaseToolkit):
    parallel_api_key: str = Field(exclude=True)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    def get_tools(self) -> List[BaseTool]:
        parallel_web_search_tool = ParallelWebTool(
            parallel_api_key=self.parallel_api_key
        )
        return [parallel_web_search_tool]
