from setuptools import setup, find_packages
import sys, os
 
version = '0.1'
 
setup(name='locust',
    version=version,
    description="Python web site load testing",
    long_description="""Locust is a python utility for doing easy, distributed load testing of a web site""",
    classifiers=[],
    keywords='',
    author='',
    author_email='',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        ],
    entry_points={
        'console_scripts': [
            'locust = locust.main:main',
        ]
    },
)
