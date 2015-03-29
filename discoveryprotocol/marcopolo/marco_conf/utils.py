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


    """def get_address(self):
        return self._address

    def set_address(self, value):
        self._address = value

    def get_email(self):
        return self._email;

    def set_email(self, value):
        self._email = value

    def __init__(self):
        self.address = property(get_address, set_address)
        self.services = property(get_services, set_services)"""

