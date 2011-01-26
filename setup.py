from setuptools import setup, find_packages
import sys, os
 
version = '0.1'
 
setup(
    name='locust',
    version=version,
    description="Python web site load testing",
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
    author='Jonatan Heyman, Carl Bystrom',
    author_email='',
    url='',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=['greenlet', 'gevent', 'flask', 'hotqueue'],
    entry_points={
        'console_scripts': [
            'locust = locust.main:main',
        ]
    },
)
