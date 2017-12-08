"""Auxiliary configurations like demuxer, udev, ..."""

from .activation import ActivationSet
from .conffile import Conffile, writeall
from .openrc import OpenRC
import subprocess
import os.path as p


class AuxiliaryConfig():

    def generate(self):
        """Should yield Conffile objects."""
        return []

    def register_iface(self, mac, name):
        pass

    def register_mux(self, vlan_id, name):
        pass


class Demux(AuxiliaryConfig):

    pass


class Mactab(AuxiliaryConfig):

    def __init__(self):
        self.macs = {}

    def register_iface(self, mac, name):
        if mac and name:
            self.macs[mac] = name

    def generate(self):
        res = ["# Managed by fc-network. Don't edit manually.\n"]
        for mac, name in sorted(self.macs.items()):
            res.append('{}\t{}\n'.format(name, mac))
        yield Conffile('mactab', ''.join(res))


class Udev(AuxiliaryConfig):

    def __init__(self):
        self.rules = {}

    def register_iface(self, mac, name):
        if not mac or not name:
            return
        if name in self.rules:
            raise RuntimeError(
                'duplicate definition of {}'.format(name))
        self.rules[name] = Conffile(
            'udev/rules.d/70-persistent-net-{}.rules'.format(name),
            'SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", '
            'ATTR{{address}}=="{}", ATTR{{type}}=="1", KERNEL=="eth*", '
            'NAME="{}"'.format(mac, name))

    def generate(self):
        for name, rule in sorted(self.rules.items()):
            yield rule


# === activation ===

# XXX refactor SimpleActivationSet (?)
class MactabActivation(ActivationSet):

    def activate(self, prefix, do_edit, do_restart):
        assert len(self.configs) == 1, "There should be exactly one mactab"
        c = self.configs[0]
        changed_config = c.write(prefix, do_edit)
        changed_inner = super().activate(prefix, do_edit, do_restart)
        if changed_config and do_restart:
            subprocess.check_call(['nameif', '-c', p.join(prefix, c.relpath)])
        return changed_config | changed_inner


class UdevActivation(ActivationSet):

    def activate(self, prefix, do_edit, do_restart):
        svcmgr = OpenRC(prefix=prefix, do=do_restart)
        changed_config = bool(writeall(self.configs, prefix, do_edit))
        changed_inner = super().activate(prefix, do_edit, do_restart)
        if changed_config and do_restart:
            svcmgr.restart(['udev-trigger'])
        return changed_config | changed_inner
