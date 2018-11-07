FROM python:3.6

RUN pip install locustio pyzmq

ADD docker_start.sh /locust-tests/docker_start.sh

WORKDIR /locust-tests

EXPOSE 8089 5557 5558

ENTRYPOINT ["./docker_start.sh"]
