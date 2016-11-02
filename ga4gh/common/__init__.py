"""
Common utilities for GA4GH software
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__version__ = "undefined"
try:
    from . import _version
    __version__ = _version.version
except ImportError:
    pass
