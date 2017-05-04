import re
from setuptools import setup


def get_version():
    content = open('redisdict/__init__.py').read()
    return re.findall(r'__version__\s*=\s*(.*)$', content)[0]


try:
    with open('README.rst') as file:
        long_description = file.read()
except:
    long_description = "Red-is-Dict, a pythonic wrapper for redis client"

setup(name='redisdict',
      version=get_version(),
      description='Pythonic wrapper for Redis Client.',
      url='https://github.com/frostming/redisdict',
      author='Frost Ming',
      author_email='mianghong@gmail.com',
      license='MIT',
      packages=['redisdict'],
      zip_safe=False,
      long_description=long_description,
      keywords='redis client mock',
      install_requires=['redis'],
      classifiers=[
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Topic :: Software Development",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: Implementation :: PyPy",
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: MIT License"
      ],
      )
