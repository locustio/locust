FROM python:3.6

RUN pip install locustio pyzmq

ADD docker_start.sh /usr/bin/docker_start
RUN chmod 755 /usr/bin/docker_start

EXPOSE 8089 5557 5558

CMD ["docker_start"]