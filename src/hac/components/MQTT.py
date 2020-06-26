import socket
import paho.mqtt.client as mqtt


class MQTT(object):
    def __init__(self, config, subscribe: list = []):
        self._subscribe = subscribe
        self._host = config['mqtt_host'] if 'mqtt_host' in config else 'localhost'
        self._user = config['mqtt_user'] if 'mqtt_user' in config else False
        self._pass = config['mqtt_pass'] if 'mqtt_pass' in config else False
        self._port = int(config['mqtt_port']) if 'mqtt_port' in config else 1883
        self._keepalive = int(config['mqtt_keepalive']) if 'mqtt_keepalive' in config else 20
        self.topic_data = {}
        self._mqttc = False
        self.connected_flag = False
        self._connect()

    def _on_message(self, client, userdata, message):
        self.topic_data[message.topic] = message.payload.decode("utf-8")

    def _connect(self):
        self._mqttc = mqtt.Client("sensor:{}".format(socket.gethostname()))
        self._mqttc.on_message = self._on_message
        if self._user and self._pass:
            self._mqttc.username_pw_set(username=self._user, password=self._pass)
        self._mqttc.connect(self._host, self._port, self._keepalive)
        self._mqttc.loop_start()
        self._mqttc.subscribe(self._subscribe)

    def publish(self, topic, value, retain=True):
        self._mqttc.publish(topic, value, retain)