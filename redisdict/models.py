"""
Python wrapper of redis datatypes
"""
from collections import MutableSet
from collections import MutableMapping
from collections import MutableSequence
try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    basestring = basestring
except NameError:
    basestring = str


class RedisType:
    def __init__(self, key, client):
        self._r = client
        self.key = key

    def _set(self, other):
        raise NotImplementedError


class HashType(RedisType, MutableMapping):
    """Dict-like wrapper for list data"""
    def __getitem__(self, key):
        if not self._r.hexists(self.key, key):
            raise KeyError(key)
        return to_value(self._r.hget(self.key, key))

    def __setitem__(self, key, value):
        self._r.hset(self.key, key, from_value(value))

    def __delitem__(self, key):
        rv = self._r.hdel(self.key, key)
        if not rv:
            raise KeyError(key)

    def __iter__(self):
        for key in self._r.hkeys(self.key):
            yield key

    def __len__(self):
        return self._r.hlen(self.key)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __repr__(self):
        return '%s value(%s)' % (self.__class__.__name__, dict(self))

    def _set(self, other):
        for key in self:
            del self[key]
        self.update(other)


class ListType(RedisType, MutableSequence):
    """List-like wrapper for list data"""
    def __setitem__(self, index, value):
        if isinstance(index, slice):
            gen = iter(value)
            indices = index.indices(len(self))
            for i in range(*indices):
                try:
                    self[i] = gen.next()
                except StopIteration:
                    # The value length is smaller than slice
                    if indices[2] != 1:
                        raise ValueError("The value length doesn't match")
                    else:
                        del self[i:indices[1]]
                        break
            else:
                # The value length is larger than slice
                i = indices[1]
                for item in gen:
                    if indices[2] != 1:
                        raise ValueError("The value length doesn't match")
                    self.insert(i, item)
                    i += 1

        elif isinstance(index, int):
            index = index + len(self) if index < 0 else index
            if index >= len(self):
                raise IndexError('Index out of range')
            self._r.lset(self.key, index, from_value(value))
        else:
            raise TypeError('list indices must be integers, not %r'
                            % type(index))

    def __getitem__(self, index):
        if isinstance(index, slice):
            indices = index.indices(len(self))
            return [self[i] for i in range(*indices)]
        elif isinstance(index, int):
            index = index + len(self) if index < 0 else index
            if index >= len(self):
                raise IndexError('Index out of range')
            return to_value(self._r.lindex(self.key, index))
        raise TypeError('list indices must be integers, not %r' % type(index))

    def __delitem__(self, index):
        if isinstance(index, slice):
            indices = index.indices(len(self))
            # reverse the indices to avoid index change.
            for i in reversed(range(*indices)):
                del self[i]
        elif isinstance(index, int):
            index = index + len(self) if index < 0 else index
            if index >= len(self):
                raise IndexError('Index out of range')
            if index == 0:
                return self._r.lpop(self.key)
            elif index == len(self) - 1:
                return self._r.rpop(self.key)
            temp = self._r.lrange(self.key, index+1, len(self))
            self._r.ltrim(self.key, 0, index-1)
            for item in temp:
                self._r.rpush(self.key, item)
        else:
            raise TypeError('list indices must be integers, not %r'
                            % type(index))

    def __len__(self):
        return self._r.llen(self.key)

    def __eq__(self, other):
        if not isinstance(other, MutableSequence):
            return False
        return list(self) == list(other)

    def __repr__(self):
        return '%s value(%s)' % (self.__class__.__name__, list(self))

    def insert(self, index, value):
        index = index + len(self) if index < 0 else index
        if index < len(self):
            if index == 0:
                return self._r.lpush(self.key, from_value(value))
            temp = self._r.lrange(self.key, index, len(self))
            self._r.ltrim(self.key, 0, index-1)
            self.append(value)
            for item in temp:
                self._r.rpush(self.key, item)
        else:
            self._r.rpush(self.key, from_value(value))

    def _set(self, other):
        self[:] = other


class SetType(RedisType, MutableSet):
    """Set-like wrapper for list data"""
    def __contains__(self, value):
        return self._r.sismember(self.key, from_value(value))

    def __iter__(self):
        for v in self._r.smembers(self.key):
            yield to_value(v)

    def __len__(self):
        return self._r.scard(self.key)

    def add(self, value):
        self._r.sadd(self.key, from_value(value))

    def discard(self, value):
        self._r.srem(self.key, from_value(value))

    def __repr__(self):
        return '%s value(%s)' % (self.__class__.__name__, list(self))

    def _set(self, other):
        for v in self:
            self.discard(v)
        for v in other:
            self.add(v)

    def _from_iterable(self, other):
        return set(other)


type_map = {'list': ListType, 'hash': HashType, 'set': SetType}


def from_value(value):
    """Convert a value to be stored in redis"""
    if isinstance(value, basestring):
        # Keep most readability, do not pickle string values
        return value
    try:
        return pickle.dumps(value)
    except Exception:
        return value


def to_value(pickled):
    """Convert a storage value from redis to human readable"""
    try:
        return pickle.loads(pickled)
    except:
        return pickled
