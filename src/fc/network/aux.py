"""Auxiliary configurations like demuxer, udev, ..."""

from .activation import ActivationSet
from .conffile import Conffile, writeall
from .openrc import OpenRC
import collections
import jinja2
import os.path as p
import subprocess


class AuxiliaryConfig():

    def __init__(self):
        self.tmpl = jinja2.Environment(
            autoescape=False,
            keep_trailing_newline=True,
            loader=jinja2.PackageLoader(__name__),
        )

    def generate(self):
        """Should yield Conffile objects."""
        return []

# XXX rename to register_mac
    def register_iface(self, mac, name):
        pass

# XXX pass VLAN object instead?
# register_mux(self, muxed_iface, demuxed_iface, vlan):
    def register_mux(self, mac, iface, vlan_id, mtu):
        pass


class Demux(AuxiliaryConfig):

    def __init__(self):
        super().__init__()
        self.vlan_by_mac = collections.defaultdict(dict)
        self.mtu = collections.defaultdict(lambda: 1280)  # reasonable minimum

    def register_mux(self, mac, iface, vlan_id, mtu=1500):
        if not mac or not iface or not vlan_id:
            return
        self.vlan_by_mac[mac][vlan_id] = iface
        if mtu > self.mtu[mac]:
            self.mtu[mac] = mtu

# XXX interface naming should be part of the policy
    def generate(self):
        for mac, vlancfg in sorted(self.vlan_by_mac.items()):
            mux_iface = 'enx{}'.format(mac).replace(':', '')
            yield Conffile(
                'conf.d/net.d/iface.' + mux_iface,
                self.tmpl.get_template('demuxer').render(
                    mux_iface=mux_iface, vlans=sorted(vlancfg.keys()),
                    names=sorted(vlancfg.items())),
                ['net.' + mux_iface])


class Mactab(AuxiliaryConfig):

    def __init__(self):
        super().__init__()
        self.macs = {}

# XXX enx$MAC for multiplexed ifaces
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
        super().__init__()
        self.rules = {}

    def register_iface(self, mac, name):
        if not mac or not name:
            return
        if name in self.rules:
            raise RuntimeError(
                'duplicate definition for {}'.format(name))
        self.rules[name] = Conffile(
            'udev/rules.d/70-persistent-net-{}.rules'.format(name),
            'SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", '
            'ATTR{{address}}=="{}", ATTR{{type}}=="1", KERNEL=="eth*", '
            'NAME="{}"'.format(mac, name))

    def generate(self):
        for name, rule in sorted(self.rules.items()):
            yield rule


# === activation ===

# XXX refactor ShellCommand (?)
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
