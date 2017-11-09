"""Network policy abstraction and templating wire-up."""


from fc.network.conffile import Conffile

import ipaddress
import jinja2


class NetworkPolicy():

    @classmethod
    def for_vlan(cls, vlan):
        if vlan.network_policy == 'untagged':
            return UntaggedPolicy(vlan)
        elif vlan.network_policy == 'tagged':
            return TaggedPolicy(vlan)
        elif vlan.network_policy == 'transit':
            return TransitPolicy(vlan)
        elif vlan.network_policy == 'ipmi':
            return IPMIPolicy(vlan)
        elif vlan.network_policy == 'puppet':
            return
        raise ValueError('unknown network policy', vlan.network_policy)

    def __init__(self, vlan):
        self.vlan = vlan
        self.tmpl = jinja2.Environment(
            autoescape=False,
            keep_trailing_newline=True,
            loader=jinja2.PackageLoader(__name__),
        )

    def extract_addrs(self):
        addresses = []
        for n, addr in self.vlan.networks.items():
            net = ipaddress.ip_network(n)
            addr = (ipaddress.ip_interface('{}/{}'.format(a, net.prefixlen))
                    for a in addr)
            addresses.extend(str(a) for a in addr)
        # filter GW list for locally configured addresses
        gateways = []
        for net, addr in self.vlan.networks.items():
            if len(addr) > 0 and net in self.vlan.gateways:
                gateways.append(self.vlan.gateways[net])
        return sorted(addresses), sorted(gateways)

    def generate(self, **kw):
        raise NotImplementedError()


class UntaggedPolicy(NetworkPolicy):

    def generate(self, mactab, udev, **kw):
        vlan = self.vlan
        addresses, gateways = self.extract_addrs()
        if vlan.bridged:
            iface = 'br' + vlan.name
            baseiface = 'eth' + vlan.name
            content = self.tmpl.get_template('iface_untagged_bridged').\
                render(iface=iface, baseiface=baseiface, vlan=vlan.name,
                       addresses=addresses, gateways=gateways, mac=vlan.mac,
                       metric=vlan.metric, mtu=vlan.mtu)
            yield Conffile('conf.d/net.d/iface.' + iface,
                           content,
                           set(['net.' + iface, 'net.' + baseiface]))
        else:
            iface = 'eth' + vlan.name
            content = self.tmpl.get_template('iface_untagged_unbridged').\
                render(iface=iface, vlan=vlan.name, mac=vlan.mac,
                       addresses=addresses, gateways=gateways,
                       metric=vlan.metric, mtu=vlan.mtu)
            yield Conffile('conf.d/net.d/iface.' + iface,
                           content, set(["net." + iface]))


class TaggedPolicy(NetworkPolicy):

    pass


class TransitPolicy(NetworkPolicy):

    pass


class IPMIPolicy(UntaggedPolicy):  # XXX is IPMI really untagged?

    pass
