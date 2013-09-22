#!/usr/bin/env python2.6

# Copyright (c) 2013, Petar Pofuk
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import os
import re
import sys
import json
import fnmatch
import commands

__all__ = ("__program__", "__url__", "__author__", "__copyright__", "__license__", "__version__", "__description__", "MainApp")

__program__ = "lbt"
__url__ = "lbt.github.io"
__author__ = "Petar Pofuk <ppofuk@gmail.com>"
__copyright__ = "Copyright (c) 2013"
__license__ = "" # TODO: which one?
__version__ = "0.0.2"
__description__ = """Tool for generating C/C++ makefiles."""


def list_iterate_directory(directory='./', sources=['*.cc'], ignores=[]):
    """
    Iterate trough directory creating sources list, where every element is
    file that satisfies unix filename pattern matching in one of elements
    in sources. Files that satisfy one element in ignores list are
    discarded.

    Args:
      directory: root directory, from where the recursion starts.
      sources: list of unix filename patterns that should be included.
      ignores: list of unix filename patterns that should be ignored.

    Returns:
      List of accepted files.
    """
    if directory[-1:] == '/':
        directory = directory[:-1]

    os.chdir(directory)

    matches = []
    for root, directory_names, file_names in os.walk(directory):
        for file_name in file_names:
            match = False
            for source in sources:
                if fnmatch.fnmatch(os.path.join(root, file_name), source):
                    match = True
            for ignore in ignores:
                #if fnmatch.fnmatch(os.path.join(root, file_name), ignore):
                #    match = False
                # We're using regex for ignores now.
                if re.match(ignore, os.path.join(root, file_name)):
                    match = False

            if match is True:
                matches.append(os.path.join(root, file_name))

    return matches


def list_dependencies(filename, command='c++ -MM'):
    """
    Parse makefile like list of dependencies given by compiler command
    and return them as list.

    Args:
      filename: File name with relative path.
      command: Compiler command that generates makefile output dependencies

    Returns:
      List of file names to whom filename is dependent.
    """
    if command != '':
        dependency = commands.getstatusoutput('%s %s%s' % (command, '',
                                              filename))
        dependency = dependency[1].split(': ')[1].split(' ')
        dependency = [item for item in dependency if item != '\\\n']

        return dependency
    else:
        return []


def give_object_name(filename):
    """
    Object name is given with following rules:
      extension (from last dot to end) is truncated,
      characters (slash, whitespace, dot) are replaced with underscore,
      extension .o is appended.

    Args:
      filename: File name with relative path.

    Returns:
      Object filename without path.
    """
    filename = filename[0:filename.rfind('.')]
    filename = filename.replace('.', '_')
    filename = filename.replace('/', '_')
    filename = filename.replace(' ', '_')
    return filename + '.o'


def list_union(first, second):
    """
    Create a union list of two lists.

    Args:
      first: First list.
      second: Second list.

    Returns:
      Union of two lists.
    """
    return list(set(first) | set(second))


class Attributed:
    """
    Class whose attributes are inherited as top objects from dict.
    """
    def __init__(self, dict):
        """
        Class constructor

        Args:
          dict: Dictionary whose top objects will be attributed to class.
        """
        self.__dict__.update(dict)
        self.__dict = dict


class SourceFile:
    """
    Hold info and operations on source file.
    """
    def __init__(self, filename, command):
        """
        Args:
          filename: File name obtained from IterateDirectory function.
          command: dependency command obtained by TargetParser.
        """
        self._filename = filename
        self._object_filename = give_object_name(filename)
        self._dependencies = list_dependencies(filename, command)

    def serialize(self):
        """
        Serialize source file info into dictionary.

        Returns:
          Dictionary with source file information.
        """
        return {self._object_filename: {'source': self._filename,
                                        'deps': self._dependencies}}

    def deserialize(data):
        """
        De-serializes data from dictionary to class.

        Args:
          data: Dictionary with with skeleton specific to SourceFile.

        Returns:
          New instance of SourceFile.
        """
        ## TODO(ppofuk): Validate dictionary
        source_file = SourceFile(data['source'], '')
        source_file._dependencies = data['dependencies']
        return source_file


class Compiler(Attributed):
    """
    Represents compiler options.
    """
    _obj_tokens = '-c -o'
    _link_tokens = '-o'
    _flag_token = '-'
    _lib_token = '-l'
    _include_token = '-I'

    def reinterpret(self, dict):
        """
        Applies new configurations from dictionary.

        Args:
          dict: Targeted dictionary with compiler rules in mind.
        """
        if 'command' in dict.keys():
            self.command = dict['command']

        if 'libs' in dict.keys():
            self.libs = list_union(self.libs, dict['libs'])

        if 'flags' in dict.keys():
            self.flags = list_union(self.flags, dict['flags'])

        if 'includes' in dict.keys():
            self.includes = list_union(self.includes, dict['includes'])

        if 'pkg_configs' in dict.keys():
            self.pkg_configs = list_union(self.pkg_configs,
                                          dict['pkg_configs'])

    def give_compile_obj(self, source):
        """
        Generates an compile string for given source.

        Args:
          source: SourceFile object.
          obj_dir: Directory where are compiled objects placed.
                   Usually in obj/.

        Returns:
          Compile string.
        """
        obj_dir = self.obj_path

        if obj_dir[-1] != "/":
            obj_dir += "/"

        def _gen_flag(in_): return self._flag_token + in_ + " "
        def _gen_lib(in_): return self._lib_token + in_ + " "
        def _gen_include(in_): return self._include_token + in_ + " "
        def _gen_pkgconf(in_): return "`pkg-config --libs --cflags " + \
                               in_ + "` "

        compile_string = self.command + " "

        for include in self.includes:
            compile_string += _gen_include(include)

        for pkgconf in self.pkg_configs:
            compile_string += _gen_pkgconf(pkgconf)

        for lib in self.libs:
            compile_string += _gen_lib(lib)

        for flag in self.flags:
            compile_string += _gen_flag(flag)

        compile_string += self._obj_tokens + " "
        compile_string += obj_dir + source._object_filename + " "
        compile_string += source._filename

        return compile_string

    def give_link_target(self):
        """
        Generates linker string for makefile.
        Skeleton of linker string is like this: $(CC) $(LIBS) -o $@ $^ $(FLAGS)

        Returns:
          Linker string.
        """
        def _gen_flag(in_): return self._flag_token + in_ + " "
        def _gen_lib(in_): return self._lib_token + in_ + " "
        def _gen_include(in_): return self._include_token + in_ + " "
        def _gen_pkgconf(in_): return "`pkg-config --libs --cflags " + \
                               in_ + "` "

        compile_string = self.command + " "

        compile_string += " -o $@ $^ "

        for pkgconf in self.pkg_configs:
            compile_string += _gen_pkgconf(pkgconf)

        for lib in self.libs:
            compile_string += _gen_lib(lib)

        for flag in self.flags:
            compile_string += _gen_flag(flag)

        return compile_string


class TargetSource(Attributed):
    """
    Description goes here. Ohnoes
    """


    def __init__(self):
        pass


    def process(self, name):
        """
        Process target source attributes. This will create dependency list and
        etc.
        """
        self._sources = []
        for source in list_iterate_directory(self.root, self.sources,
                                             self.ignores):
            self._sources.append(SourceFile(source, self.dependency_command))

        self._compiler = Compiler(self.compiler)
        self._name = name

    def give_makefile(self):
        """
        Generate makefile string.

        Returns:
          Generated makefile string.
        """
        if self._compiler.obj_path[-1] != '/':
            self._compiler.obj_path += '/'

        # Regex for depends
        after = re.compile('after:')

        makefile_str = ""
        makefile_str = self.target + ": "

        if "depends" in self.__dict__:
            for depend in self.depends:
                if after.match(depend):
                    continue
                else:
                    makefile_str += depend + " "

        for source in self._sources:
            makefile_str += self._compiler.obj_path + source._object_filename
            makefile_str += " "

        if "depends" in self.__dict__:
            for depend in self.depends:
                if after.match(depend):
                    depend = depend.replace(after.pattern, '')
                    makefile_str += depend + " "

        makefile_str += "\n\t"
        makefile_str += self._compiler.give_link_target()
        makefile_str += "\n\n"

        for source in self._sources:
            makefile_str += self._compiler.obj_path + source._object_filename
            makefile_str += ": "
            makefile_str += " ".join(source._dependencies)
            makefile_str += "\n\t"
            makefile_str += self._compiler.give_compile_obj(source)
            makefile_str += "\n\n"

        return makefile_str


class Recipe:


    def __init__(self):
        _targets = []
        _defines = []


    def open_file(self, filename):
        """
        Loads JSON recipe and parses it.

        Args:
          open: file name string
        """
        
        recipe = None
        with open(filename, "r") as f:
            recipe = json.loads(f.read())

        
        for target in recipe:
            if "type" in recipe[target] and target != "defines":
                if recipe[target]['type'] == "source":
                    self._targets.append(TargetSource(recipe[target]))
                    self._targets[-1].process(target)
                elif recipe[target]['type'] == "exec":
                    self._targets.append(TargetExecute(recipe[target]))
                    self._targets[-1].process(target)


        if "defines" in recipe:
            self._defines = recipe['defines']


    def give_makefile(self):
        """
        Generates makefile string.

        Returns:
          Makefile string.
        """
        makefile_str = ""
        makefile_str += "\n".join(self._defines)
        makefile_str += "\n\n"

        for target in self._targets:
            makefile_str += target.give_makefile()

        return makefile_str


class TargetExecute(Attributed):
    """
    Handler for generating only execute targets.
    """

    def process(self, name):
        self._name = name

    def give_makefile(self):
        """
        Generates makefile target.

        Returns:
          Generated makefile.
        """
        makefile_str = self._name + ": "
        if "depends" in self.__dict__:
            makefile_str += " ".join(self.depends)

        makefile_str += "\n\t"
        makefile_str += "\n\t".join(self.commands)
        makefile_str += "\n\t"

        return makefile_str + "\n"



class MainApp:

    
    def __init__(self, opts):
        self._opts = opts
        
        if self._opts.make_makefile:
            _recipe = Recipe().open_file(self._opts.make_makefile)
            # TODO(ppofuk): recipe validator
            # TODO(sam): call recipe validator here
            self.make_makefile()

        if self._opts.new_project:
            self.new_project()
            

    def make_makefile(self):
        try:
            with open("makefile", "w") as f:
                f.write(self._recipe.give_makefile())
            print(" [+] Makefile generated successfully.")
        except IOError:
            print(" [-] There was an error while generating makefile. Try again, or report issue.")
            

    def new_project(self):
        """Generate new project from template"""
        # TODO(sam): generate project structure
        # TODO(sam): download testing lib for project
        pass

    def new_library(self):
        """Generate new library from template""" 
        pass
