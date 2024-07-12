import os
import subprocess
from shutil import which
from sys import exit


def build() -> None:
    if os.environ.get("SKIP_PRE_BUILD", "") == "true":
        print("Skipping front end build...")
        return
    if which("yarn") is None:
        print(
            "Locust requires the yarn binary to be available in this shell to build the web front-end.\nSee: https://docs.locust.io/en/stable/developing-locust.html#making-changes-to-locust-s-web-ui"
        )
        exit(1)
    print("Building front end...")
    use_shell = os.name == 'nt'
    subprocess.run(["yarn", "webui:install"], shell=use_shell)
    subprocess.run(["yarn", "webui:build"], shell=use_shell)


if __name__ == "__main__":
    build()
