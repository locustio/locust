import os
import subprocess


def build() -> None:
    if os.environ.get("SKIP_PRE_BUILD", "") == "true":
        print("Skipping front end build...")
        return
    print("Building front end...")
    subprocess.run(["make", "frontend_build"], shell=True)


if __name__ == "__main__":
    build()
