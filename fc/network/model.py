import ipaddress as ip
import re


class Port:

    def __init__(self, enc):
        self.name = str(enc['port'])
        # check name for kernel compatibility
        if not re.match(r'^[a-z0-9]{1,5}$', self.name):
            raise ValueError('invalid port name', self.name)
        self.mac = str(enc.get('mac', ''))
        if self.mac == '00:00:00:00:00:00':  # legacy directory data
            self.mac = ''
        self.vlans = {name: VLAN(name, v) for name, v in enc['vlans'].items()}

        # at least one VLAN runs as tagged
        self.tagged = any(v.tagged for v in self.vlans.values())

        self.lowlevel_name = 'eth' + (
            next(iter(self.vlans)) if not self.tagged and self.vlans
            else self.name)

        # port name / VLAN name collision?
        if self.tagged and any(v == self.name for v in self.vlans):
            raise ValueError(self.name)

    @property
    def mtu_max(self):
        """Returns the maximum MTU of all attached VLANs.

        Defaults to 1500 if there are no VLANs configured.
        """
        if not self.vlans:
            return 1500
        return max(v.mtu for v in self.vlans.values())

    @property
    def conffile_name(self):
        """Name of the configuration file in /etc/conf.d/net.d."""
        return 'iface.' + self.lowlevel_name

    @property
    def service_names(self):
        """All associated OpenRC services (net.*)"""
        svc = set(['net.' + self.conffile_name])
        for vlan in self.vlans:
            svc.update(vlan.services)
        return svc


class VLAN:

    def __init__(self, name, enc):
        self.name = name
        self.mode = str(enc.get('mode', 'static'))
        self.bridged = bool(enc.get('bridged', False))
        self.metric = int(enc.get('metric', 1000))
        self.mtu = int(enc.get('mtu', 1500))
        self.tagged = bool(enc.get('tagged', False))
        self.vlanid = int(enc.get('vlanid', 0))
        self.networks = dict(enc.get('networks', {}))
        self.gateways = [ip.ip_address(g) for g in enc.get('gateways', [])]
        if self.tagged and not self.vlanid:
            raise RuntimeError('must specify vlanid for tagged VLAN', name)

    @property
    def interface_name(self):
        """Network interface on which IP addresses are configured.

        This name may be the same as lowlevel_name in case the
        interfaces is neither bridged nor tagged.
        """
        if self.bridged:
            return 'br' + self.name
        return 'eth' + self.name

    @property
    def bridgebase_name(self):
        """Name of the attached base device (e.g., ethXXX) on bridges.

        If the network is tagged, this is the name of the demultiplexed
        VLAN interface.
        """
        return 'eth' + self.name

    @property
    def addresses(self):
        """All configured interface addresses in CIDR notation."""
        for n, addrs in sorted(self.networks.items()):
            net = ip.ip_network(n)
            for a in addrs:
                yield ip.ip_interface('{}/{}'.format(
                    a, net.prefixlen))

    @property
    def nets(self):
        """All mentioned CIDR networks sorted alphabetically."""
        return (ip.ip_network(n) for n in sorted(self.networks.keys()))

    @property
    def used_nets(self):
        """CIDR networks which has at least one local IP address."""
        return (ip.ip_network(n) for n, addrs in sorted(self.networks.items())
                if addrs)

    @property
    def services(self):
        """Associated OpenRC services."""
        return set(['net.' + self.interface_name])
