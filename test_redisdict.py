#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for RedisDict"""
from redisdict import RedisDict
from fakeredis import FakeStrictRedis
import unittest
import datetime
import pytest
from collections import Set, MutableSequence

now = datetime.datetime.now()
golden = {'a': 'hello',
          'b': True,
          'c': 1,
          'd': None,
          'e': now,
          'f': range(5),
          'g': dict(zip('abcd', range(4))),
          'h': set(['a', 'b', 'c'])}


def cmp_no_order(seq1, seq2):
    """Compare two sequences regardless of order"""
    if len(seq1) != len(seq2):
        return False
    temp = seq2[:]
    for i in seq1:
        try:
            temp.remove(i)
        except ValueError:
            return False
    return len(temp) == 0


class RedisDictTestCase(unittest.TestCase):
    def setUp(self):
        global redis

        redis = RedisDict(prefix='test', client=FakeStrictRedis)
        redis.update(golden)

    def tearDown(self):
        redis._r.flushall()

    def test_prefix(self):
        """Test the key is prefixed correctly"""
        for c in 'abcdefgh':
            key = 'test.' + c
            assert redis._r.exists(key)

    def test_contains(self):
        for c in 'abcdefgh':
            assert c in redis

    def test_get_item(self):
        assert redis['d'] is None
        assert redis.get('a') == 'hello'
        with pytest.raises(KeyError):
            redis['z']

    def test_iter_item(self):
        assert dict(redis) == golden

    def test_keys(self):
        assert cmp_no_order(redis.keys(), list('abcdefgh'))

    def test_set_item(self):
        redis['a'] = 'hello michael'
        assert redis['a'] == 'hello michael'
        assert redis.setdefault('i', 1.2) == 1.2
        assert 'i' in redis

    def test_set_different_type(self):
        redis['b'] = [1, 2, 3]
        assert isinstance(redis['b'], MutableSequence)
        redis['f'] = 'hello'
        assert redis['f'] == 'hello'
        redis['g'] = set([1, 2, 3])
        assert isinstance(redis['g'], Set)

    def test_del_item(self):
        del redis['a']
        assert 'a' not in redis
        with pytest.raises(KeyError):
            del redis['z']

    def test_get_attribute(self):
        assert redis.f == range(5)
        redis['get'] = 1
        assert callable(redis.get)

    def test_list_get_item(self):
        data = redis['f']
        assert data[1] == 1
        with pytest.raises(IndexError):
            data[10]
        with pytest.raises(TypeError):
            data['1']

    def test_list_get_slice(self):
        data = redis['f']
        assert data[2:] == [2, 3, 4]
        assert data[:-2] == [0, 1, 2]
        assert data[1:4:2] == [1, 3]

    def test_list_contains(self):
        data = redis['f']
        assert 1 in data
        assert 'a' not in data

    def test_list_set_item(self):
        data = redis['f']
        data[1] = 4
        assert redis['f'] == [0, 4, 2, 3, 4]
        data[-1] = 1
        assert redis['f'] == [0, 4, 2, 3, 1]
        with pytest.raises(IndexError):
            data[10] = 10
        with pytest.raises(TypeError):
            data['1'] = 1

    def test_list_set_slice(self):
        data = redis['f']
        data[1:3] = ['a', 'b']
        assert redis['f'] == [0, 'a', 'b', 3, 4]
        data[1:1] = ['c', 'd']
        assert redis['f'] == [0, 'c', 'd', 'a', 'b', 3, 4]
        data[:] = [1, 2, 3]
        assert redis['f'] == [1, 2, 3]
        data[::2] = ['a', 'b']
        assert redis['f'] == ['a', 2, 'b']
        with pytest.raises(ValueError):
            # target length < source length and step != 1
            data[::2] = [1]
        with pytest.raises(ValueError):
            # target length > source length and step != 1
            data[::2] = [1, 3, 5]
        with pytest.raises(ValueError):
            # target length != source length and step != 1
            data[::-1] = [1, 3]

    def test_list_del_item(self):
        data = redis['f']
        del data[1]
        assert len(redis['f']) == 4
        del data[-1]
        assert redis['f'] == [0, 2, 3]
        with pytest.raises(IndexError):
            del data[10]
        with pytest.raises(TypeError):
            del data['1']

    def test_list_del_slice(self):
        data = redis['f']
        del data[1:1]
        assert len(redis['f']) == 5
        del data[1:5:2]
        assert redis['f'] == [0, 2, 4]
        del data[:]
        assert len(redis['f']) == 0

    def test_list_insert(self):
        data = redis['f']
        data.insert(0, 'a')
        assert data == ['a', 0, 1, 2, 3, 4]
        data.insert(2, 'b')
        assert data == ['a', 0, 'b', 1, 2, 3, 4]
        data.insert(10, 'c')
        assert data == ['a', 0, 'b', 1, 2, 3, 4, 'c']

    def test_list_append_pop(self):
        data = redis['f']
        data.append('a')
        assert data.pop() == 'a'
        assert data.pop(0) == 0
        assert len(data) == 4
