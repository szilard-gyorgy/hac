import smbus
import re


class Relay(object):
    def __init__(self, board, config, i2c_bus=1, i2c_addr=0x10):
        self.labels = {}
        self._board = smbus.SMBus(i2c_bus)
        self._i2c_addr = i2c_addr
        
        # load labels
        for key, value in config.items(): 
            match = (re.match(r"^relay_{}_(\d+)$".format(board), key))
            if match:
                self.labels[value[0]] = match.group(1)

    def switch_on(self, relay):
        print("Switch ON relay:{}".format(self.labels[relay]))
        self._board.write_byte_data(self._i2c_addr, int(self.labels[relay]), 0xFF)

    def switch_off(self, relay):
        print("Switch OFF relay:{}".format(self.labels[relay]))
        self._board.write_byte_data(self._i2c_addr, int(self.labels[relay]), 0x00)
