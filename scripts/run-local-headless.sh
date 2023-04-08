#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

script_dir="$(realpath "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )")"
root_dir="$(realpath "${script_dir}/..")"

pushd "${root_dir}"
"${VIRTUAL_ENV}/bin/pip" install --editable .
popd

pushd "${script_dir}"
"${VIRTUAL_ENV}/bin/python" -m locust \
  --locustfile "${script_dir}/locustfile.py" \
  --headless \
  --host "https://example.com" \
  --loglevel "INFO"
popd
