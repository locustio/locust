# Stage 1: Build web front end
FROM node:20.0.0-alpine AS webui-builder

ADD locust/webui locust/webui
ADD package.json .

# long yarn timeout necessary in certain network environments
RUN yarn webui:install --production --network-timeout 60000
RUN yarn webui:build

# Stage 2: Build Locust package
FROM python:3.11-slim AS base

FROM base AS builder
RUN apt-get update && apt-get install -y git 
# there are no wheels for some packages (geventhttpclient?) for arm64/aarch64, so we need some build dependencies there
RUN if [ -n "$(arch | grep 'arm64\|aarch64')" ]; then apt install -y --no-install-recommends gcc python3-dev; fi
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV SKIP_PRE_BUILD="true"
COPY . /build
WORKDIR /build
# bring in the prebuilt front-end before package installation
COPY --from=webui-builder locust/webui/dist locust/webui/dist
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry self add "poetry-dynamic-versioning[plugin]" && \
    poetry build -f wheel && \
    pip install dist/*.whl

# Stage 3: Runtime image
FROM base
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
# turn off python output buffering
ENV PYTHONUNBUFFERED=1
RUN useradd --create-home locust
# ensure correct permissions
RUN chown -R locust /opt/venv
USER locust
WORKDIR /home/locust
EXPOSE 8089 5557
ENTRYPOINT ["locust"]

