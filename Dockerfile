FROM python:3.6.6-alpine3.8

RUN apk --no-cache add g++ \ 
      && pip install locustio pyzmq

EXPOSE 8089 5557 5558

ENTRYPOINT ["/usr/local/bin/locust"]
