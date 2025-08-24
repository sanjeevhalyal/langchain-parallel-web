from typing import List

from langchain_core.tools import BaseTool

from langchain_parallel_web.toolkits import ParallelWebToolkit
from langchain_parallel_web.tools import ParallelWebTool


def test_toolkit_returns_tool_instance() -> None:
    toolkit = ParallelWebToolkit(parallel_api_key="dummy-key")
    tools: List[BaseTool] = toolkit.get_tools()

    assert len(tools) == 1
    assert isinstance(tools[0], ParallelWebTool)


def test_tool_from_toolkit_has_expected_interface() -> None:
    toolkit = ParallelWebToolkit(parallel_api_key="dummy-key")
    tool = toolkit.get_tools()[0]

    # Basic interface checks that do not require network access
    assert isinstance(tool.name, str) and tool.name
    assert isinstance(tool.description, str) and tool.description
    # Args schema should expose required fields
    fields = set(tool.args_schema.model_fields.keys())
    assert {"objective", "search_queries"}.issubset(fields)
