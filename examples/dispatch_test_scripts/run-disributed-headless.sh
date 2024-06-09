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

pids=()

function cleanup(){
  for pid in ${pids}
  do
    echo "Killing worker with pid ${pid}"
    kill -9 "${pid}" || echo "Failed killing worker with pid ${pid}"
  done
}

trap cleanup EXIT

export LOCUST_WORKER_ADDITIONAL_WAIT_BEFORE_READY_AFTER_STOP=5

n_workers=4

for n in $(seq 1 ${n_workers})
do
  tmp_file="$(mktemp /tmp/locust-worker-${n}.log.XXXXXX)"
  echo "Starting worker ${n} (logs in ${tmp_file})"
  "${VIRTUAL_ENV}/bin/python" -m locust \
    --locustfile "${script_dir}/locustfile.py" \
    --host "https://example.com" \
    --worker \
    --master-host "0.0.0.0" \
    --master-port "5557" \
    --logfile "${tmp_file}" \
    --loglevel "DEBUG" &
  pids+=($!)
done

echo "Starting master"
"${VIRTUAL_ENV}/bin/python" -m locust \
  --locustfile "${script_dir}/locustfile.py" \
  --host "https://example.com" \
  --headless \
  --master \
  --master-bind-host "0.0.0.0" \
  --master-bind-port "5557" \
  --expect-workers ${n_workers} \
  --loglevel "DEBUG"

popd
