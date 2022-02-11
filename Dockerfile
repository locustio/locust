FROM python:3.9-slim

COPY . /build
RUN apt update && apt install -y --no-install-recommends git gcc python3-dev \
    && cd /build && pip install --no-cache . \
    && apt purge -y --auto-remove -y gcc && apt clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

EXPOSE 8089 5557

RUN useradd --create-home locust
USER locust
WORKDIR /home/locust
ENTRYPOINT ["locust"]

# turn off python output buffering
ENV PYTHONUNBUFFERED=1
