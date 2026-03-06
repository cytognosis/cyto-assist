from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("cyto-assist")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["__version__"]
