import ipaddress


class VLAN():

    def __init__(self, name, enc, staticcfg):
        self.name = name
        self.network_policy = enc.get('network_policy') or 'puppet'
        self.mac = enc['mac'].lower() or '00:00:00:00:00:00'
        self.networks = enc.get('networks', {})
        self.gateways = enc.get('gateways', {})
        self.staticcfg = staticcfg
        self._addresses = []
        self._networks = []
        for n, addr in sorted(self.networks.items()):
            net = ipaddress.ip_network(n)
            addr = (ipaddress.ip_interface('{}/{}'.format(a, net.prefixlen))
                    for a in addr)
            self._addresses.extend(addr)
            self._networks.append(net)

    def __str__(self):
        return 'VLAN({})'.format(self.__dict__)

    def addrs(self, ipvers=None):
        if ipvers:
            return [a for a in self._addresses if a.version == ipvers]
        return self._addresses

    def nets(self, ipvers=None):
        if ipvers:
            return [n for n in self._networks if n.version == ipvers]
        return self._networks

    @property
    def bridged(self):
        return self.staticcfg.getboolean('bridged')

    @property
    def mtu(self):
        return self.staticcfg.getint('mtu', 1500)

    @property
    def vlan_id(self):
        return self.staticcfg.getint('vlan_id')

    @property
    def metric(self):
        return self.staticcfg.getint('metric', 1000)
