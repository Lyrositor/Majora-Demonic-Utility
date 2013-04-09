#!/usr/bin/env python3
from distutils.core import setup, Extension

simpleEnc = Extension("simpleEnc", sources=["simpleEnc.c"])

setup(name = "simpleEnc",
      version = "1.0",
      description = "A simple encoding scheme.",
      ext_modules = [simpleEnc])
