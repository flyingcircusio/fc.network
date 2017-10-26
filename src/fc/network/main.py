"""Flying Circus network configuration utility."""

import ipaddress
import itertools
import jinja2


class Conffile():

    def __init__(self, relpath, content, svc=set()):
        """Describes a configuration file with associated services.

        relpath: file path relative to the conf root (e.g., /etc)
        content: text
        svc: set of services that must be restarted if file contents
            have changed.
        """
        self.relpath = relpath
        self.content = content
        self.svc = svc


def extract_addrs(ifcfg):
    addresses = []
    for n, addr in ifcfg['networks'].items():
        n = ipaddress.ip_network(n)
        addr = (ipaddress.ip_interface('{}/{}'.format(a, n.prefixlen))
                for a in addr)
        addresses.extend(str(a) for a in addr)
    # filter GW list for locally configured addresses
    gateways = []
    for n, addr in ifcfg['networks'].items():
        if len(addr) > 0 and n in ifcfg['gateways']:
            gateways.append(ifcfg['gateways'][n])
    return addresses, gateways


class AttrDict(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


class VLAN(AttrDict):

    def __init__(self, name, enc, static):
        super().__init__(enc)
        self.name = name
        self.mac = self.mac.lower() or '00:00:00:00:00:00'
        self.static = static
        if 'network_policy' not in self.__dict__ or not self.network_policy:
            self.network_policy = 'puppet'  # classic

    def __str__(self):
        return 'VLAN({})'.format(self.__dict__)


class NetworkPolicy():

    @classmethod
    def for_vlans(cls, vlans):
        vlans = list(vlans)  # could be an iterator
        policies = set(vlan.network_policy for vlan in vlans)
        if len(policies) != 1:
            raise RuntimeError(
                'cannot have different network policies for the same '
                'mac address', vlans)
        policy = policies.pop()
        if policy == 'untagged':
            return UntaggedPolicy(vlans)
        elif policy == 'tagged':
            return TaggedPolicy(vlans)
        elif policy == 'transit':
            return TransitPolicy(vlans)
        elif policy == 'ipmi':
            return IPMIPolicy(vlans)
        raise ValueError('unknown network policy', policy)

    def __init__(self, vlans):
        self.tmpl = jinja2.Environment(
            loader=jinja2.PackageLoader(__name__),
            autoescape=False
        )
        self.vlans = vlans


class UntaggedPolicy(NetworkPolicy):

    def __init__(self, vlans):
        super().__init__(vlans)
        if len(vlans) != 1:
            raise RuntimeError(
                'cannot have more than one untagged VLAN on one interface',
                vlans)

    def conffiles(self):
        return []
# XXX
        for vlan, ifcfg in self.param.interfaces.values():
            if vlan == 'ipmi':
                continue
            addresses, gateways = extract_addrs(ifcfg)
            if ifcfg['bridged']:
                iface = 'br' + vlan
                baseiface = 'eth' + vlan
                content = self.tmpl.get_template('iface_untagged_bridged').\
                    render(iface=iface, baseiface=baseiface, cfg=ifcfg,
                           vlan=vlan, addresses=addresses, gateways=gateways)
                yield Conffile('conf.d/net.d/iface.' + iface,
                               content,
                               set(iface, baseiface))
            else:
                iface = 'eth' + vlan
                content = self.tmpl.get_template('iface_untagged_unbridged').\
                    render(iface=iface, cfg=ifcfg, vlan=vlan,
                           addresses=addresses, gateways=gateways)
                yield Conffile('conf.d/net.d/iface.' + iface,
                               content,
                               set(iface))
# XXX


class TaggedPolicy(NetworkPolicy):

    pass


class TransitPolicy(NetworkPolicy):

    pass


class IPMIPolicy(UntaggedPolicy):  # XXX is IPMI really untagged?

    pass


def netcfg(networkcfg, name):
    if name in networkcfg:
        return networkcfg[name]
    return networkcfg[networkcfg.default_section]


def parse_interfaces(enc_ifaces, networkcfg):
    vlans = sorted(
        [VLAN(name, enc, netcfg(networkcfg, name))
         for name, enc in enc_ifaces.items()],
        key=lambda v: v.mac)
    return {
        mac: NetworkPolicy.for_vlans(vlans)
        for mac, vlans in itertools.groupby(vlans, lambda v: v.mac)
    }


def main(enc, networkcfg, dry_run, no_restart, etc='/etc'):
    return parse_interfaces(enc['parameters']['interfaces'], networkcfg)
