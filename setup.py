#!/usr/bin/env python2

import src
from distutils.core import setup

setup(name = src.__program__,
      version = src.__version__,
      description = src.__description__,
      url = src.__url__,
      author = src.__author__,
      author_email = src.__author__,
      package_dir = {"": "src"},
      scripts = ["src/lbt"],
      packages=[""]) 