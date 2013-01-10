# encoding: utf-8

from setuptools import setup, find_packages
import sys, os

version = '0.6.2'

setup(
    name='locustio',
    version=version,
    description="Website load testing framework",
    long_description="""Locust is a python utility for doing easy, distributed load testing of a web site""",
    classifiers=[
        "Topic :: Software Development :: Testing :: Traffic Generation",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
    ],
    keywords='',
    author='Jonatan Heyman, Carl Bystrom, Joakim Hamrén, Hugo Heyman',
    author_email='',
    url='http://locust.io',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=["gevent>=0.13", "flask>=0.8", "requests==0.14.1"],
    entry_points={
        'console_scripts': [
            'locust = locust.main:main',
        ]
    },
    test_suite='locust.test.runtests',
)
