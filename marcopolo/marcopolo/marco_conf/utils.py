__author__ = 'martin'


class Node:
    def __init__(self, address=None, services=[], multicast_group = None):
        self._address = address
        self._services = services
        self._multicast_group = multicast_group

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = value

    @property
    def services(self):
        return self._services

    @services.setter
    def services(self, value):
        self._services = value


    @property
    def multicast_group(self):
        return self._multicast_group

    @multicast_group.setter
    def multicast_group(self, value):
        self._multicast_group = value

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, value):
        self._params = value