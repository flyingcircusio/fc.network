"""Flying Circus network configuration utility."""

import glob
import os
import os.path as p
import jinja2
import ipaddress


class Conffile():

    def __init__(self, relpath, content, svc):
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



class NetworkPolicy():

    @classmethod
    def select(cls, policy, param):
        if policy == 'untagged':
            return UntaggedPolicy(param)
        elif policy == 'tagged':
            return TaggedPolicy(param)
        elif policy == 'transit':
            return TransitPolicy(param)
        raise ValueError('unknown network policy', policy)

    def __init__(self):
        self.tmpl = jinja2.Environment(
            loader=jinja2.PackageLoader(__name__),
            autoescape=False
        )


class UntaggedPolicy(NetworkPolicy):

    def __init__(self, param):
        super().__init__()
        self.param = param
        # ensure unique mac addresses

    def conffiles(self):
        for vlan, ifcfg in self.param.interfaces.values():
            if vlan == 'ipmi':
                continue
            addresses, gateways = extract_addrs(ifcfg)
# XXX per-vlan network policy
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


def main(enc, dry_run, no_restart, etc='/etc'):
    conffiles = []
    param = enc['parameters']
# XXX generate conffiles from param
