from importlib.metadata import version, PackageNotFoundError


__all__ = ["get_version", "__version__"]


def get_version():
    try:
        return version("jlatrading")
    except PackageNotFoundError:
        return "0.0.0"


__version__ = get_version()
