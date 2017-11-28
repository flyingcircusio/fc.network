"""Auxiliary configurations like demuxer, udev, ..."""

from .conffile import Conffile


class AuxiliaryConfig():

    def register_iface(self, relpath, values, services):
        pass

    def generate(self):
        """Should yield Conffile objects."""
        raise NotImplementedError()


class Demux(AuxiliaryConfig):

    pass


class Udev(AuxiliaryConfig):

    def __init__(self):
        self.rules = {}

    def register_iface(self, relpath, values, services):
        mac = values.get('mac', '')
        iface = values.get('baseiface', values.get('iface', ''))
        if not mac or not iface:
            return
        if iface in self.rules:
            raise RuntimeError(
                'duplicate definition of {}'.format(iface), values)
        self.rules[iface] = Conffile(
            'rules.d/70-persistent-net-{}.rules'.format(iface),
            'SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", '
            'ATTR{{address}}=="{}", ATTR{{type}}=="1", KERNEL=="eth*", '
            'NAME="{}"'.format(mac, iface))

    def generate(self):
        for iface, rule in sorted(self.rules.items()):
            yield rule
