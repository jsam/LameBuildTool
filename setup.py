#!/usr/bin/env python2

import os
import sys
import src
from distutils.core import setup


def generate_data_files(*dirs):
    results = []
    for src_dir in dirs:
        for root, dirs, files in os.walk(src_dir):
            results.append((
                sys.prefix 
                + "/share/" 
                + src.__program__ 
                + "/"  + root, 
                map(lambda f: root + "/" + f, files)))
    return results


setup(name = src.__program__,
      version = src.__version__,
      description = src.__description__,
      url = src.__url__,
      author = src.__author__,
      author_email = src.__author__,
      packages = ["", ""],
      package_dir = {"": "src"},
      data_files = generate_data_files("templates"),
      #package_data = {"": ["src/templates.tar.gz"]},
      scripts = ["src/lbtcli"]) 

