FROM python:3.6.6-alpine3.8

RUN apk --no-cache add g++ \
      && apk --no-cache add zeromq-dev \
      && pip install locustio pyzmq

COPY docker_start.sh docker_start.sh
RUN chmod +x docker_start.sh

EXPOSE 8089 5557 5558

ENTRYPOINT ["./docker_start.sh"]
