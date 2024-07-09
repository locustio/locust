import os
import subprocess
from sys import exit
from shutil import which


def build() -> None:
    if which("yarn") is None:
        print("Locust requires the yarn binary to be available in this shell to build the web front-end.\nSee: https://docs.locust.io/en/stable/developing-locust.html#making-changes-to-locust-s-web-ui")
        exit(1)
    if os.environ.get("SKIP_PRE_BUILD", "") == "true":
        print("Skipping front end build...")
        return
    print("Building front end...")
    subprocess.run(["make", "frontend_build"])


if __name__ == "__main__":
    build()
