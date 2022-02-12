FROM python:3.9-slim

COPY . /build

# there are no wheels for some packages (maybe geventhttpclient?) for arm64, so we need gcc there
RUN export ARM=$(arch | grep arm64)

RUN apt update && apt install -y git && \
    if [ -n "$ARM" ]; then apt install -y --no-install-recommends gcc python3-dev; fi && \
    cd /build && pip install --no-cache . && \
    if [ -n "$ARM" ]; then apt purge -y --auto-remove -y gcc python3-dev; fi && \
    apt clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

EXPOSE 8089 5557

RUN useradd --create-home locust
USER locust
WORKDIR /home/locust
ENTRYPOINT ["locust"]

# turn off python output buffering
ENV PYTHONUNBUFFERED=1
