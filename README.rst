Redis Wrapper
=============
.. image:: https://img.shields.io/pypi/v/rediswrapper.svg
  :target: https://pypi.python.org/pypi/rediswrapper
.. image:: https://img.shields.io/pypi/pyversions/rediswrapper.svg
  :target: https://pypi.python.org/pypi/rediswrapper
.. image:: https://travis-ci.org/frostming/rediswrapper.svg?branch=master
  :target: https://travis-ci.org/frostming/rediswrapper
.. image:: https://coveralls.io/repos/github/frostming/rediswrapper/badge.svg?branch=master
  :target: https://coveralls.io/github/frostming/rediswrapper?branch=master

*rediswrapper is a pythonic wrapper of Redis Client for end users. The whole storage
acts like a python dict as well as its child storage values.*

Features
--------
* The root client support dict-like operations
* Python object wrappers for list, set, hash type values
* Implicit serialization and deserialization when storing and fetching data

Installation
------------
From PyPI::

  pip install rediswrapper

From GitHub::

  git clone https://github.com/frostming/rediswrapper
  cd rediswrapper
  python setup.py install


Usage
-----

``rediswrapper`` will try to serialize non-sting values and store them in redis and
deserialize them when fetching back.

All redis value types are mocked with respective python objects and support all
standard methods as the builtin types.

.. code:: python

  >>> import rediswrapper
  >>> redis = rediswrapper.RedisDict()
  # String value
  >>> redis['a'] = 'hello'
  # int value
  >>> redis['b'] = 2
  >>> dict(redis)
  {'a': 'hello', 'b': 2}
  # Picklable object
  >>> import datetime
  >>> redis['c'] = datetime.datetime.now()
  # List value
  >>> redis['d'] = list(range(5))
  >>> redis['d'].append(0)
  >>> redis['d']
  ListType value([0, 1, 2, 3, 4, 0])
  # Hash value
  >>> redis['e'] = {'a': 1, 'b': 2}
  >>> redis['e'].get('a')
  1
  # Set value
  >>> redis['f'] = set([1, 2])
  >>> redis['f'].add(3)
  >>> redis['f']
  SetType value([1, 2, 3])

To inspect those value types, one should use the ABCs defined in ``collections``
module.

.. code:: python

  >>> from collections import Mapping
  >>> isinstance(redis['e'], Mapping)
  True
