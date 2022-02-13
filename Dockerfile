FROM python:3.9-slim as base
FROM base as builder

RUN apt update && apt install -y git 

# there are no wheels for some packages (geventhttpclient?) for arm64/aarch64, so we need some build dependencies there
RUN if [ -n "$(arch | grep 'arm64\|aarch64')" ]; then apt install -y --no-install-recommends gcc python3-dev; fi

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . /build
RUN pip install /build/

FROM base
ENV PATH="/opt/venv/bin:$PATH"
COPY --from=builder /opt/venv /opt/venv

EXPOSE 8089 5557
# turn off python output buffering
ENV PYTHONUNBUFFERED=1
RUN useradd --create-home locust
USER locust
WORKDIR /home/locust
ENTRYPOINT ["locust"]
