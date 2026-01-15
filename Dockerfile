# This is a local-use Docker image which illustrates the end-to-end build process for Locust

# Stage 1: Build web front end
FROM node:22.0.0-alpine AS webui-builder

ADD locust/webui locust/webui
ADD package.json .

# long yarn timeout necessary in certain network environments
RUN yarn webui:install --production --network-timeout 60000
RUN yarn webui:build

# Stage 2: Build Locust package (make sure any changes here are also reflected in Dockerfile.ci)
FROM python:3.13-slim AS base

FROM base AS builder
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates git \
    gcc g++ make \
    python3-dev
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV SKIP_PRE_BUILD="true"
COPY . /build
WORKDIR /build
# clear locally built assets, dist remains part of the docker context for CI purposes
RUN rm -rf dist
# bring in the prebuilt front-end before package installation
COPY --from=webui-builder locust/webui/dist locust/webui/dist

# Build the Python project
ENV UV_PROJECT_ENVIRONMENT="/opt/venv"
ADD https://astral.sh/uv/0.7.2/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"
RUN uv build && \
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
# perform initial bytecode compilation (brings down total startup time from ~0.9s to ~0.6s)
RUN locust --version
USER locust
WORKDIR /home/locust
EXPOSE 8089 5557
ENTRYPOINT ["locust"]
