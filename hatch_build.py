import os
import shutil
import subprocess
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface  # type: ignore


class BuildFrontend(BuildHookInterface):
    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        # Only build the front end once, in the source dist, the wheel build just copies it from there
        if self.target_name == "sdist":
            print("Building front end...")
            try:
                subprocess.check_output("yarn install", cwd="locust/webui", shell=True, stderr=subprocess.STDOUT)
                subprocess.check_output("yarn build", cwd="locust/webui", shell=True, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"'{e.cmd}' got exit code {e.returncode}: {e.output}")

            return super().initialize(version, build_data)
