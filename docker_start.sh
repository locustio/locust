#!/usr/bin/env sh

if [ -z "${TARGET_URL}" ]; then
  echo "ERROR: TARGET_URL not configured" >&2
  exit 1
fi

LOCUST_MODE="${LOCUST_MODE:=standalone}"
_LOCUST_OPTS="-f ${LOCUSTFILE_PATH:-/locustfile.py} -H ${TARGET_URL}"

if [ "${LOCUST_MODE}" = "master" ]; then
    _LOCUST_OPTS="${_LOCUST_OPTS} --master"
elif [ "${LOCUST_MODE}" = "worker" ]; then
    if [ -z "${LOCUST_MASTER_HOST}" ]; then
        echo "ERROR: MASTER_HOST is empty. Worker mode requires a master" >&2
        exit 1
    fi

    _LOCUST_OPTS="${_LOCUST_OPTS} --worker --master-host=${LOCUST_MASTER_HOST} --master-port=${LOCUST_MASTER_PORT:-5557}"
fi

echo "Starting Locust in ${LOCUST_MODE} mode..."
echo "$ locust ${LOCUST_OPTS} ${_LOCUST_OPTS}"

exec locust ${LOCUST_OPTS} ${_LOCUST_OPTS}
