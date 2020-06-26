#!/usr/bin/env python3

#import smbus2
from smbus import SMBus
import paho.mqtt.client as mqtt
import socket
import time
import sys 
import re
import json 

class I2CRelayBoard:
    """Represents an PCF8574 I2C relay board"""
    def __init__(self, i2c_bus, i2c_addr):
        self._i2c_bus = i2c_bus
        self._i2c_addr = i2c_addr

        self._i2c = SMBus(i2c_bus)
        self._state = self._i2c.read_byte(self._i2c_addr)

    def _commit_state (self):
        self._i2c.write_byte(self._i2c_addr, self._state)

    def is_on(self, relay_number):
        return not(self._state >> relay_number-1) & 1

    def switch_all_off(self):
        self._state = 0b11111111
        self._commit_state()

    def switch_all_on(self):
        self._state = 0b00000000
        self._commit_state()

    def switch_on(self, relay_number):
        self._state &= ~(1 << relay_number-1)
        self._commit_state()

    def switch_off(self, relay_number):
        self._state |= (1 << relay_number-1)
        self._commit_state()

    def toggle(self, relay_number):
        if self.is_on(relay_number):
            self.switch_off(relay_number)
        else:
            self.switch_on(relay_number)

###setup mqtt helper functions 
def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("connected OK")
        mqttc.subscribe([(i,0) for i in relays.keys()]) 
    else:
        print("Bad connection Returned code=",rc)

def on_message(client, userdata, message):
    if message.topic in relays:
      if int(message.payload):
        print ("ON: ", relays[message.topic])
        board.switch_on(relays[message.topic])
      else:
        print ("OFF: ", relays[message.topic])
        board.switch_off(relays[message.topic])
      
I2C_BUS = 1
I2C_ADDR = 0x20
MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_USER = "ha_remote_sensor"
MQTT_PASS = "qq5z3WX2yZdfPGT9"
MQTT_KEEPALIVE = 30

relays = {
  "home/aquarium/switch/water_heater": 1,
  "home/aquarium/switch/plant_heater": 2,
  "home/aquarium/switch/aq_air_pump": 3,
  "home/aquarium/switch/aq_plant_light": 4,
  "home/aquarium/switch/aq_natural_light": 5,
  "home/aquarium/switch/aq_co2_main": 6,
  "home/aquarium/switch/aq_co2_boost": 7,
  "home/aquarium/switch/aq_wchange_pump": 8
}

board = I2CRelayBoard(I2C_BUS, I2C_ADDR)

mqttc = mqtt.Client(socket.gethostname() +'-relay_daemon')
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username=MQTT_USER,password=MQTT_PASS)
mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
mqttc.loop_start()
mqttc.loop_forever()
