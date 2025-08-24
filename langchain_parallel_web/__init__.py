from importlib import metadata

from langchain_parallel_web.toolkits import ParallelWebToolkit
from langchain_parallel_web.tools import ParallelWebTool

try:
    __version__ = metadata.version(__package__)  # type: ignore[reportTypeError]
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""
del metadata  # optional, avoids polluting the results of dir(__package__)

__all__ = [
    "ParallelWebToolkit",
    "ParallelWebTool",
    "__version__",
]
