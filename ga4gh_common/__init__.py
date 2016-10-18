"""
Common utilities for GA4GH software
"""
__version__ = "undefined"
try:
    from . import _version
    __version__ = _version.version
except ImportError:
    pass
