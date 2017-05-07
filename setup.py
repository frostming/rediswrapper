import re
import sys
import os
from setuptools import setup


if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    sys.exit()

if sys.argv[-1] == 'test':
    try:
        __import__('py')
    except ImportError:
        print('pytest required.')
        sys.exit(1)

    errors = os.system('py.test')
    sys.exit(bool(errors))


def get_version():
    content = open('rediswrapper/__init__.py').read()
    return re.findall(r'__version__\s*=\s*[\'"](.*)[\'"]', content)[0]

readme = 'README'
for name in os.listdir('.'):
    if name.startswith('README'):
        readme = name
        break
try:
    with open(readme) as file:
        long_description = file.read()
except:
    long_description = "RedisWrapper, a pythonic wrapper for redis client"

setup(name='rediswrapper',
      version=get_version(),
      description='Pythonic wrapper for Redis Client.',
      url='https://github.com/frostming/rediswrapper',
      author='Frost Ming',
      author_email='mianghong@gmail.com',
      license='MIT',
      packages=['rediswrapper'],
      test_suite='test_rediswrapper',
      zip_safe=False,
      long_description=long_description,
      keywords='redis client mock',
      test_requires=['pytest', 'fakeredis'],
      install_requires=['redis'],
      classifiers=[
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Topic :: Software Development",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: Implementation :: CPython",
          "Programming Language :: Python :: Implementation :: PyPy",
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: MIT License"
      ],
      )
