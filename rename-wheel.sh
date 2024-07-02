#!/bin/bash

# When using build script in poetry, the wheel file is named with the architecture and python version
# This script renames the wheel file to a generic, multi-arch name
# From https://github.com/python-poetry/poetry/issues/3509#issuecomment-1483859472

wheel_file=$(find dist/ -type f -name '*.whl')
new_wheel_file=$(echo ${wheel_file} | sed "s/-cp[0-9].*$/-py3-none-any.whl/")

echo "Renaming ${wheel_file} to ${new_wheel_file}"
mv ${wheel_file} ${new_wheel_file}
