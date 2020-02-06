FROM python:3.6-alpine as builder

RUN apk --no-cache add g++ zeromq-dev libffi-dev
COPY . /src
WORKDIR /src
RUN pip install .

FROM python:3.6-alpine

RUN apk --no-cache add zeromq && adduser -s /bin/false -D locust
COPY --from=builder /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages
COPY --from=builder /usr/local/bin/locust /usr/local/bin/locust
COPY docker_start.sh docker_start.sh
RUN chmod +x docker_start.sh

EXPOSE 8089 5557

USER locust
CMD ["./docker_start.sh"]
