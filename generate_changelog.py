import subprocess

github_api_token = input("Enter Github API token: ")
version = input("Enter Locust version number (--future-release argument): ")

cmd = [
    "github_changelog_generator",
    "-t", github_api_token,
    "-u", "locustio", "-p", "locust",
    "--exclude-labels", "duplicate,question,invalid,wontfix,cantfix",
    "--future-release", version,
]

print("Running command: %s\n" % " ".join(cmd))
subprocess.run(cmd)
