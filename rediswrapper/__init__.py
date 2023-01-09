"""
rediswrapper
------------
A pythonic wrapper for redis client.

Author: Frost Ming<mianghong@gmail.com>
"""

__version__ = "0.4.0.post1"
__all__ = ["RedisDict"]

from .storage import RedisDict
