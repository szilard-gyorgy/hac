import socket
import paho.mqtt.client as mqtt


class MQTT(object):
    def __init__(self, config, onmessage=False, subscribe: list = [], type: str = 'sensor'):
        print("Loading")
        self.topic_data = {}
        self._host = config['mqtt_host'] if 'mqtt_host' in config else 'localhost'
        self._user = config['mqtt_user'] if 'mqtt_user' in config else False
        self._pass = config['mqtt_pass'] if 'mqtt_pass' in config else False
        self._port = int(config['mqtt_port']) if 'mqtt_port' in config else 1883
        self._keepalive = int(config['mqtt_keepalive']) if 'mqtt_keepalive' in config else 20
        self.subscribe = subscribe

        self._mqttc = mqtt.Client("{}:{}".format(type, socket.gethostname()))
        self._mqttc.on_connect = self._on_connect
        self._mqttc.on_message = onmessage if onmessage else self._on_message
        if self._user and self._pass:
            self._mqttc.username_pw_set(username=self._user, password=self._pass)
        self._mqttc.connect(self._host, self._port, self._keepalive)
        self._mqttc.loop_start()
        

    def _on_connect(self, client, userdata, flags, rc):
        if rc==0:
            print("connected OK")
            self._mqttc.subscribe(self.subscribe)
        else:
            print("Bad connection Returned code=",rc)


    def _on_message(self, client, userdata, message):
        self.topic_data[message.topic] = message.payload.decode("utf-8")

    def publish(self, topic, payload, retain=True):
        print(payload)
        if not isinstance(payload, bool):
            self._mqttc.publish(topic, payload, retain=True)

    def loop_forever(self):
        self._mqttc.loop_forever()

    def disconnect(self):
        self._mqttc.disconnect()
