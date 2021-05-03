import subprocess
import os

github_api_token = (
    os.getenv("CHANGELOG_GITHUB_TOKEN") if os.getenv("CHANGELOG_GITHUB_TOKEN") else input("Enter Github API token: ")
)
version = input("Enter Locust version number (--future-release argument): ")

cmd = [
    "github_changelog_generator",
    "-t",
    github_api_token,
    "-u",
    "locustio",
    "-p",
    "locust",
    "--exclude-labels",
    "duplicate,question,invalid,wontfix,cantfix,stale",
    "--future-release",
    version,
]

print("Running command: %s\n" % " ".join(cmd))
subprocess.run(cmd)
