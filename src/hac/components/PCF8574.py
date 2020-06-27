from hac.libs.i2crelay.i2crelay import I2CRelayBoard
import re


class Relay(object):
    def __init__(self, board, config, i2c_bus=1, i2c_addr=0x20):
        self.labels = {}
        self.board = I2CRelayBoard(i2c_bus, i2c_addr)

        # load labels
        for key, value in config.items():
            match = (re.match(r"^relay_{}_(\d+)$".format(board), key))
            if match:
                self.labels[value[0]] = match.group(1)

    def switch_on(self, relay):
        self.board.switch_on(self.label[relay])

    def switch_off(self, relay):
        self.board.switch_on(self.label[relay])
