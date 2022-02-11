FROM python:3.9-slim

RUN apt-get update && apt-get install -y git gcc python3-dev && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
COPY . /build
RUN cd /build && pip install --no-cache . && rm -rf /build

EXPOSE 8089 5557

RUN useradd --create-home locust
USER locust
WORKDIR /home/locust
ENTRYPOINT ["locust"]

# turn off python output buffering
ENV PYTHONUNBUFFERED=1
