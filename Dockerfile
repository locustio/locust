FROM python:3.8

COPY . /src
WORKDIR /src
RUN pip install .
RUN rm -rf /src

EXPOSE 8089 5557

RUN useradd --create-home locust
USER locust
ENTRYPOINT ["locust"]

# turn off python output buffering
ENV PYTHONUNBUFFERED=1
