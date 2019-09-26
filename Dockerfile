FROM python:3.6.6-alpine3.8 as builder

RUN apk --no-cache add g++ zeromq-dev
RUN pip install locustio pyzmq

FROM python:3.6.6-alpine3.8

RUN apk --no-cache add zeromq-dev
COPY --from=builder /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages
COPY --from=builder /usr/local/bin/locust /usr/local/bin/locust
COPY docker_start.sh docker_start.sh
RUN chmod +x docker_start.sh

EXPOSE 8089 5557 5558

ENTRYPOINT ["./docker_start.sh"]
