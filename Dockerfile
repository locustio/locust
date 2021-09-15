FROM python:3.8

COPY . /build
RUN cd /build && git status && git describe --dirty --tags --long --match *[0-9]* && pip install . && rm -rf /build

EXPOSE 8089 5557

RUN useradd --create-home locust
USER locust
WORKDIR /home/locust
ENTRYPOINT ["locust"]

# turn off python output buffering
ENV PYTHONUNBUFFERED=1
