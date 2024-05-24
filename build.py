import subprocess


def build() -> None:
    print("Building front end...")
    subprocess.run(["make", "frontend_build"])


if __name__ == "__main__":
    build()
