
# changelog 
## betterstubs branch
- createstubs  - version 1.3.16
    - fix for 1.16 
    - skip _test modules in module list
    - black formatting 
    - addition of __init__ methods ( based on runtime / static)
    - class method decorator 
    - additional type information for constants using comment style typing
    - detect if running on MicroPython or CPython
    - improve report formatting to list each module on a separate line to allow for better comparison

- create stubs from micropython documentation
    - Read the micropython library documentation files 
    - Extract 
        modules
            functions
            classes  (some classes are described as functions and need to be hoisted up to a class)
                methods
                class methods
                static methods
            exceptions
    - extract the relevant docstrings
    - determine the return type of a function or method based on the docstring 
        this is about 60% accurate 


- workflows
    - move to ubuntu 20.04 
        - move to test/tools/ubuntu_20_04/micropython_v1.xx
    - run more tests in GHA 

- postprocessing 
    - minification adjusted to work with `black`
    - use `mypy.stubgen` to generate stubs 
    - remove dependency and 'make_stub_files.py' as this is no longer maintained and has several issues.
    - run per folder 
        - verify 1:1 relation .py-.pyi
        - run `mypy.stubgen` to generate missing .pyi files
    - publish test results to GH



- develop / repo setup
    - updated dev requirements (requirements-dev.txt)
    - seperate install needed for:
        - git 2.23 .0 or newer (git switch)
        - pyright via npm install (and thus npm)
    - switched to using submodules to remove  external dependencies
        how to clone : 
        `git submodule init`
        `git submodule update`
    - enable developing on [GitHub codespaces](https://github.com/codespaces)
        - add configuration for codespaces 
        - devcontainer
            - installs pyright ( via `npm install -g pyright`)
            - starts .devcontainer/setup.h
        - setup.sh 
            - initializes the submodules 
            - installs python requirements-dev.txt 
            - installs python requirements-dev.txt 

    - added black configuration file to avoid running black on minified version
    - switched to using .venv on all platforms
    - added and improved tests
        - test coverage increased to 82%
    - move to test/tools/ubuntu_20_04/micropython_v1.xx
        - for test (git workflows)
        - for tasks 
    - make use of CPYTHON stubs to alle makestubs to run well on CPYTHON
        - allows pytest, and debugging of tests
    - add tasks to :
        - run createstubs in linux version
`
    - 

