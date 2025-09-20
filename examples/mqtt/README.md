# MQTT Load testing with Locust

## Prerequisites

Have access to a running mqtt broker.

```bash
# start mosquitto locally
# the configuration file is required to start 
# WINDOWS
docker run -d -p 1883:1883 --name mqtt-broker -v .\\examples\\mqtt\\mosquitto_config\\mosquitto.conf:/mosquitto/config/mosquitto.conf eclipse-mosquitto:latest
# UNIX
docker run -d -p 1883:1883 --name mqtt-broker -v ./examples/mqtt/mosquitto_config/mosquitto.conf:/mosquitto/config/mosquitto.conf eclipse-mosquitto:latest
```

Install Locust with MQTT support:

```bash
# Using pip
pip install locust[mqtt]
```

## Usage

```bash
# Run simple example without web UI
locust -f examples/mqtt/locustfile.py --headless
# Run simple custom client example without web UI
locust -f examples/mqtt/locustfile_custom_mqtt_client.py --headless
```

