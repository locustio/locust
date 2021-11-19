# -*- coding: utf-8 -*-
import ast
import os
import re
import sys

from setuptools import find_packages, setup

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

setup(
    name="locust",
    install_requires=[
        "gevent>=20.9.0",
        "flask>=2.0.0",
        "Werkzeug>=2.0.0",
        "requests>=2.23.0",
        "msgpack>=0.6.2",
        "pyzmq>=22.2.1",
        "geventhttpclient>=1.5.1",
        "ConfigArgParse>=1.0",
        "psutil>=5.6.7",
        "Flask-BasicAuth>=0.2.0",
        "Flask-Cors>=3.0.10",
        "roundrobin>=0.0.2",
        "typing-extensions>=3.7.4.3",
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
    use_scm_version={
        "write_to": "locust/_version.py",
        "local_scheme": "no-local-version",
    },
    setup_requires=["setuptools_scm"],
)
