import os
import paho.mqtt.client as mqtt
from low_voltage.utils.logger import logger


# mqtt_host = os.environ["MQTT_HOST"]
def connect_to_mqtt():
    mqtt_host = os.environ.get("MQTT_HOST")
    if mqtt_host is None:
        logger.error("MQTT_HOST environment variable is not set.")
        return

    def on_connect(client, userdata, flags, rc):
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        logger.info(f"connected to mqtt broker: {mqtt_host}")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(mqtt_host, 1883, 60)
    return client
