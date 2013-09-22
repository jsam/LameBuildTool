LameBuildTool
=============

A simple tool for auto-generating C/C++ makefiles and project management.

!Note, that this is a rough raw unstable version.

Installation
------------

Installation is done via distutils which is part of standard library in Python, so you can just execute:

    sudo python2 setup.py install

or(depends on your alias for python)

    sudo python setup.py install

This will install library to:

    /usr/lib/python2.7/site-packages

executable script to:
    
    /usr/bin/

and template resources to:

    /usr/lbt/templates/library/*
    /usr/lbt/templates/project/*


* Remember that current version is supported only with Python2.
* If you are using python2 with alias "python" you need to switch shebang values inside those scripts otherwise you will get errors.


Usage
-----

Generate makefile

    lbtcli -m [recipe.json]

Generate project structure from template

    lbtcli -np [path/where/to/generate/project] 

To update makefile in given project you can use:

    lbtcli -m . # or ./ 

Generate library structure from template

    lbtcli -nl [path/to/existing/project]



Recipes for sources
-------------------
Recipe is a build definition in JSON.
A skeleton for typical executable looks something like this:
```JSON
{
    "target_name": {
        "type": "source",
        "depends": [
            "some_other_target_definition"
        ],
        "root": "./",
        "target": "bin/target_name",
        "sources" : [
            "*.cc",
            "src/base/event.cc"
        ],
        "ignores": [
            "src/main.cc"
        ],
        "dependency_command": "c++ -MM",
        "compiler": {
            "command": "c++",
            "libs": [
                "pthread",
                "png"
            ],
            "flags": [
                "ggdb",
                "static"
            ],
            "includes": [
                "third-party/"
            ],
            "pkg_configs": [
                "cairo",
                "gtk"
            ],
            "obj_path": "obj/"
        }
    }
}
```

Keep in mind a few thing. All the listed field should be in the recipe file, because the validation phase is in TODO :)

Every target in name must be named. In the showed skeleton a target is named as target_name:
    ```"target_name": { ...
    }```

Each target has it's type. Type is either:
    ```"type": "source"```
for generating C/C++ makefile with dependencies and other rule sets for C/C++ binary, or
    ```"type": "exec"```
for just executing a given command (this is still being tested and has a major bug that breaks things. Sorry).

You may define more targets in recipe. Dependency in on target to other targets is defined in list
```JSON
"depends": [
    "target1",
    "after:target2",
    ...
  ]
  ```
If the depending target is of type source add the targets target field value (for example "bin/target_name").
On exec targets add their target name (the root value).
Adding after keyword is for source targets only, and it will add the given dependency to the end in linking stage.

The target field defines the final linked binary path.
    "target": "bin/target_name"

Sources and ignores are two lists in which the source files are defined. All sources are matched with unix filename pattern matching. So you can define something like *.c which will include all c files recursively in the defined root directory. Ignores are matched with regex!

dependency_command defines a command which will be executed on every matched source file. The executed command MUST return a makefile valid syntax dependency list.

Compiler options are defined under "compiler" object. Don't add tokens as -l or - for flags and libs. The script automatically adds them.
You can control the prefix tokens with the following fields (the presented values are their defaults):
```JSON
"compiler": {
    ...
    "_flag_token": "-",
    "_lib_token": "-l",
    "_include_token": "-I"
}
```

obj_path defines the directory where the temporary *.o files are placed.
Support for compiling libraries and other things is in TODO. For now you can the configure the flags with these options:
```JSON
"compiler": {
...
    "_obj_tokens": "-c -o",
    "_link_tokens": "-o"
...
}
```

Recipe for exec
---------------
```JSON
"some_name": {
        "type": "exec",
        "depends": [
            "some_name"
        ],
        "commands": [
            "command1",
            "command2"
        ]
    }
```

Adding makefile definitions
----------------------------
The ```"defines"``` root field is a list in which every element is a makefile variable that is added to the begging of makefile.
For example:
```JSON
"defines": [
    ".DEFAULT_GOAL := bin/some_target"
]
```
will define bin/some_target as default target when calling ```make```.
Use this in example if you use ```exec``` types recipes in conjunction with ```source``` recipes so you can define a default.

TODO
----
- [x] get drunk (bug found: infinite iteration ongoing in head object at 0x0)
- [ ] get the batmobile back (https://fbcdn-sphotos-d-a.akamaihd.net/hphotos-ak-prn1/524514_626427844064708_686258337_n.jpg)
- [ ] validate JSON with lbt rules before loading it
- [ ] support for compiling libraries
- [ ] parsing command line options (yeah, I'm lazy, argv ftw!)
- [ ] support for loading more recipes
- [ ] fix exec and dependencies with source
- [ ] do some tests
- [ ] eval field with syntax something like this:
      ```...
      "eval": [
        ["python-command that evals", {target redefinition if eval is true}]
      ]```

