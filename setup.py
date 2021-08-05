# -*- coding: utf-8 -*-
import ast
import os
import re
import sys

from setuptools import find_packages, setup

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

# parse version from locust/__init__.py
_version_re = re.compile(r"__version__\s+=\s+(.*)")
_init_file = os.path.join(ROOT_PATH, "locust", "__init__.py")
with open(_init_file, "rb") as f:
    version = str(ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1)))

setup(
    name="locust",
    version=version,
    install_requires=[
        "gevent>=20.9.0",
        "flask>=2.0.0",
        "Werkzeug>=2.0.0",
        "requests>=2.9.1",
        "msgpack>=0.6.2",
        "pyzmq>=22.2.1",
        "geventhttpclient>=1.4.4",
        "ConfigArgParse>=1.0",
        "psutil>=5.6.7",
        "Flask-BasicAuth>=0.2.0",
        "Flask-Cors>=3.0.10",
        "roundrobin>=0.0.2",
    ],
    test_suite="locust.test",
    tests_require=[
        "cryptography",
        "mock",
        "pyquery",
    ],
    extras_require={
        ":sys_platform == 'win32'": ["pywin32"],
    },
)
