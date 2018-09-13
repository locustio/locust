FROM python:3.6-alpine

RUN apk --no-cache add g++
RUN pip install locustio pyzmq

EXPOSE 8089 5557 5558

ENTRYPOINT ["/usr/local/bin/locust"]
