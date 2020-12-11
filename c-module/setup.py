# This Python file uses the following encoding: utf-8
from distutils.core import setup, Extension

def main():
    setup(name="simplemodule", version="1.0.0", description="todo",
        author="Ilian Zapryanov", author_email="heatblazer@gmail.com",
        ext_modules=[Extension("simplemodule", ["simplemodule.c"])])

if __name__ == "__main__":
    main()
