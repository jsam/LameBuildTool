#!/usr/bin/env python2
import sys
from buildtool import *

if sys.platform == "win32":
        project = BuildToolProject.Autogenerate('example.exe', './', BuildToolProfile.FromFile('bin_cc'))
else:
        project = BuildToolProject.Autogenerate('example', './', BuildToolProfile.FromFile('bin_cc'))

project.MakeMakefile()
