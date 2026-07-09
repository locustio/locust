#!/usr/bin/env python3

import os
import subprocess
import sys

github_api_token = os.getenv("CHANGELOG_GITHUB_TOKEN") or input("Enter Github API token: ")

if len(sys.argv) < 2:
    raise Exception("Provide a version number as parameter (--future-release argument)")

version = sys.argv[1]

cmd = [
    "github_changelog_generator",
    "-t",
    github_api_token,
    "-u",
    "locustio",
    "-p",
    "locust",
    "--exclude-labels",
    "duplicate,question,invalid,wontfix,cantfix,stale,no-changelog",
    "--header-label",
    "# Also see https://github.com/locustio/locust/releases",
    "--since-tag",
    "2.35.0",
    # "--since-commit", # these cause issues
    # "2020-07-01 00:00:00",
    "--future-release",
    version,
]

print(f"Running command: {' '.join(cmd)}\n")
subprocess.run(cmd)
