"""
Mocker class of redis-py client
"""
import redis
from .models import type_map
from .models import from_value, to_value
from collections import MutableMapping


class RedisDict(MutableMapping):
    """ The mocker class of redis-py client, support dict-like APIs and
    attribute assignments.

    The construction arguments are the same as redis-py, except for ``client``
    which represents the client class and defaults to ``redis.StrictRedis``.

    The class also subclasses dict to enable subclass or isinstance check.
    """
    def __init__(self, host='localhost', port=6379, db=0, *args, **kwargs):
        client_cls = kwargs.pop('client', redis.StrictRedis)
        self.prefix = kwargs.pop('prefix', 'root') + '.'
        self._r = client_cls(host, port, db, *args, **kwargs)

    def __getitem__(self, key):
        rkey = self.prefix + key
        if not self._r.exists(rkey):
            raise KeyError(key)
        if self._r.type(rkey) == 'string':
            return to_value(self._r.get(rkey))
        else:
            return self._wrap_type(rkey, self._r.type(rkey))

    def __contains__(self, key):
        return self._r.exists(self.prefix + key)

    def __setitem__(self, key, value):
        try:
            del self[key]
        except KeyError:
            pass
        rkey = self.prefix + key
        if isinstance(value, list):
            rv = self._wrap_type(rkey, 'list')
            rv._set(value)
        elif isinstance(value, dict):
            rv = self._wrap_type(rkey, 'hash')
            rv._set(value)
        elif isinstance(value, set):
            rv = self._wrap_type(rkey, 'set')
            rv._set(value)
        else:
            rv = from_value(value)
            self._r.set(rkey, rv)

    def __delitem__(self, key):
        if key not in self:
            raise KeyError(key)
        rkey = self.prefix + key
        self._r.delete(rkey)

    def _wrap_type(self, key, type):
        return type_map[type](key, self._r)

    def __iter__(self):
        for key in self._r.keys():
            if key.startswith(self.prefix):
                yield key[len(self.prefix):]

    def __len__(self):
        return len(self._r.keys())

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)
