FROM python:3.8 as builder

COPY . /src
WORKDIR /src
RUN pip install .


FROM python:3.8

COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
COPY --from=builder /usr/local/bin/locust /usr/local/bin/locust

EXPOSE 8089 5557

RUN useradd --create-home locust
USER locust
ENTRYPOINT ["locust"]

# turn off python output buffering
ENV PYTHONUNBUFFERED=1
