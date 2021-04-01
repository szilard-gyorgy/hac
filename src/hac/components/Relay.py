import re


class Relay(object):
    def __init__(self, type, i2c_bus=1, i2c_addr=False):

        self.type = type

        if self.type == 'pcf8574':
            from hac.libs.i2crelay.i2crelay import I2CRelayBoard

            self.i2c_addr = i2c_addr if i2c_addr else 0x20
            self._board = I2CRelayBoard(i2c_bus, i2c_addr)

        elif self.type == 'DockerPi':
            import smbus

            self.i2c_addr = i2c_addr if i2c_addr else 0x10
            self._board = smbus.SMBus(i2c_bus)

        elif self.type == 'GPIO':
            import RPi.GPIO as GPIO
            self._board = GPIO
            self._board.setmode(GPIO.BCM)
            self._board.setwarnings(False)
            self.gpio_map = (19, 26, 20, 21, 16, 13, 6, 5)

    def switch(self, position, relay):
        print ("Switch {} relay: {}".format(position, relay))

        if self.type == 'pcf8574':
            self._board.switch_on(relay) if position == 'on' else self.board.switch_off(self.label[relay])
        elif self.type == 'DockerPi':
            position_data = 0xFF if position == 'on' else 0x00
            self._board.write_byte_data(self._i2c_addr, relay, position_data)
        elif self.type == 'GPIO':
            position_data = self._board.LOW if position == 'on' else self._board.HIGH
            print("GPIO{}".format(self.gpio_map[relay-1]))
            self._board.setup(self.gpio_map[relay-1], self._board.OUT)
            self._board.output(self.gpio_map[relay-1], position_data)

    def switch_on(self, relay):
        self.switch("on", relay)

    def switch_off(self, relay):
        self.switch("off", relay)
