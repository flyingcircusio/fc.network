"""Network policy abstraction and templating wire-up."""

from .conffile import Conffile
from .vlan import VLAN
import jinja2


class NetworkPolicy():
    """Coordinates a single VLAN's network configurations."""

    @classmethod
    def build(cls, name, enc, networkcfg):
        """Returns network policies + VLANS for enc interfaces."""
        static = (networkcfg[name] if name in networkcfg
                  else networkcfg[networkcfg.default_section])
        vlan = VLAN(name, enc, static)
        if vlan.network_policy == 'untagged':
            return UntaggedPolicy(vlan)
        elif vlan.network_policy == 'tagged':
            return TaggedPolicy(vlan)
        elif vlan.network_policy == 'transit':
            return TransitPolicy(vlan)
        elif vlan.network_policy == 'ipmi':
            return IPMIPolicy(vlan)
        elif vlan.network_policy == 'puppet':
            return cls()
        raise ValueError('unknown network policy', vlan.network_policy)

    def __init__(self, vlan):
        self.vlan = vlan
        self.tmpl = jinja2.Environment(
            autoescape=False,
            keep_trailing_newline=True,
            loader=jinja2.PackageLoader(__name__),
        )
        self.callbacks = []

    def register(self, callbacks):
        self.callbacks.extend(callbacks)

    def generate(self):
        """Returns list/generator of Conffiles.

        To be overriden in subclasses.
        """
        return []

    def _conffile(self, relpath, templates, values, services):
        """Wrapper for template generation."""
        for cb in self.callbacks:
            cb.register_iface(
                values['mac'], values.get('baseiface', values.get('iface')))
        out = ''.join(self.tmpl.get_template(t).render(**values)
                      for t in templates)
        return Conffile(relpath, out, set(services))


class UntaggedPolicy(NetworkPolicy):

    def generate(self):
        vlan = self.vlan
        name = self.vlan.name
        v = dict(
            iface='eth' + name, vlan=name,
            addresses=vlan.addrs(), addr4=vlan.addrs(4), addr6=vlan.addrs(6),
            nets=vlan.nets(), nets4=vlan.nets(4), nets6=vlan.nets(6),
            gateways=vlan.gateways_filtered(), mac=vlan.mac,
            metric=vlan.metric, mtu=vlan.mtu,
        )
        if vlan.bridged:
            v['baseiface'] = v['iface']
            v['iface'] = 'br' + name
            yield self._conffile(
                'conf.d/net.d/iface.br' + name,
                ['iface_untagged_common', 'iface_untagged_bridged'], v,
                ['net.br' + name, 'net.eth' + name])
        else:
            yield self._conffile(
                'conf.d/net.d/iface.eth' + name,
                ['iface_untagged_common', 'iface_untagged_unbridged'], v,
                ['net.eth' + name])


class TaggedPolicy(NetworkPolicy):

    pass


class TransitPolicy(NetworkPolicy):

    pass


class IPMIPolicy(NetworkPolicy):  # XXX is IPMI tagged or untagged?

    pass
