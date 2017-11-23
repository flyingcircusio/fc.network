"""Network policy abstraction and templating wire-up."""

from fc.network.conffile import Conffile
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

    def gateways_filtered(self):
        gateways = []
        for net, addr in self.vlan.networks.items():
            if len(addr) > 0 and net in self.vlan.gateways:
                gateways.append(self.vlan.gateways[net])
        return sorted(gateways)

    def conffile(self, relpath, templates, values, services):
        """Wrapper for template generation."""
        out = ''.join(self.tmpl.get_template(t).render(**values)
                      for t in templates)
        return Conffile(relpath, out, set(services))

    def generate(self, **kw):
        raise NotImplementedError()


class UntaggedPolicy(NetworkPolicy):

    def generate(self, **kw):
        vlan = self.vlan
        name = self.vlan.name
        v = dict(
            iface='eth' + name, vlan=name,
            addresses=vlan.addrs(), addr4=vlan.addrs(4), addr6=vlan.addrs(6),
            nets=vlan.nets(), nets4=vlan.nets(4), nets6=vlan.nets(6),
            gateways=self.gateways_filtered(), mac=vlan.mac,
            metric=vlan.metric, mtu=vlan.mtu,
        )
        if vlan.bridged:
            v['baseiface'] = v['iface']
            v['iface'] = 'br' + name
            yield self.conffile(
                'conf.d/net.d/iface.br' + name,
                ['iface_untagged_common', 'iface_untagged_bridged'], v,
                ['net.br' + name, 'net.eth' + name])
        else:
            yield self.conffile(
                'conf.d/net.d/iface.eth' + name,
                ['iface_untagged_common', 'iface_untagged_unbridged'], v,
                ['net.eth' + name])


class TaggedPolicy(NetworkPolicy):

    pass


class TransitPolicy(NetworkPolicy):

    pass


class IPMIPolicy(UntaggedPolicy):  # XXX is IPMI really untagged?

    pass
