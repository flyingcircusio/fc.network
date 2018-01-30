"""Auxiliary configurations like demuxer, udev, ..."""

from .conffile import Conffile
import collections
import jinja2

HEADER = "# Managed by fc-network. Don't edit manually.\n"


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

    def register_mac(self, mac, name):
        pass

    def register_mux(self, mux_iface, vlan):
        pass


class Demux(AuxiliaryConfig):

    def __init__(self):
        super().__init__()
        self.mtu = collections.defaultdict(lambda: 1280)  # reasonable minimum
        self.ifaces = collections.defaultdict(dict)

    def register_mux(self, mux_iface, vlan):
        if not mux_iface or not vlan:
            return
        self.ifaces[mux_iface][vlan.vlan_id] = vlan
        if vlan.mtu > self.mtu[mux_iface]:
            self.mtu[mux_iface] = vlan.mtu

    def generate(self):
        for mux_iface, cfg in sorted(self.ifaces.items()):
            yield Conffile(
                'conf.d/net.d/iface.' + mux_iface,
                self.tmpl.get_template('demuxer').render(
                    mux_iface=mux_iface,
                    vlan_ids=sorted(cfg.keys()),
                    names=sorted((i, v.basename) for i, v in cfg.items()),
                    mtu=self.mtu[mux_iface]),
                {'net.' + mux_iface})


class MaclikeConfig(AuxiliaryConfig):
    """Kind of config that manages mac addresses (mactab, udev)."""

    def __init__(self):
        super().__init__()
        self.macs = {}

    def register_mac(self, mac, name):
        if mac and name:
            self.macs[mac] = name

    def generate(self):
        res = [HEADER]
        for mac, name in sorted(self.macs.items()):
            res.append(self.TEMPLATE.format(name=name, mac=mac))
        yield Conffile(self.RELPATH, ''.join(res))


class Mactab(MaclikeConfig):

    RELPATH = 'mactab'
    TEMPLATE = '{name}\t{mac}\n'


class Udev(MaclikeConfig):

    RELPATH = 'udev/rules.d/71-persistent-net.rules'
    TEMPLATE = ('SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", '
                'ATTR{{address}}=="{mac}", ATTR{{type}}=="1", KERNEL=="eth*", '
                'NAME="{name}"\n')
