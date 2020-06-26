import re
from sensor.libs.AtlasI2C.AtlasI2C import AtlasI2C


class AtlasPH(object):
    def __init__(self, address):
        self._device = AtlasI2C()
        self._device.set_i2c_address(address)

    def readPH(self):
        return float(re.sub("[^0-9,\.]", "", self._device.query("R").split(" ")[3]))

    def query(self, query):
        return self._device.query(query)

