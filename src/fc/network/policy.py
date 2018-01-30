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
        if vlan.policy == 'untagged':
            return UntaggedPolicy(vlan)
        elif vlan.policy == 'tagged':
            return TaggedPolicy(vlan)
        elif vlan.policy == 'transit':
            return TransitPolicy(vlan)
        elif vlan.policy == 'ipmi':
            return IPMIPolicy(vlan)
        elif vlan.policy == 'puppet':
            raise RuntimeError(
                'should never been called with "puppet" policy', vlan)
        raise ValueError(
            'unknown network policy for VLAN {}'.format(vlan.name),
            vlan.policy)

    def __init__(self, vlan):
        self.vlan = vlan
        self.tmpl = jinja2.Environment(
            autoescape=False,
            keep_trailing_newline=True,
            loader=jinja2.PackageLoader(__name__),
        )
        self.callbacks = []

    def common_values(self):
        """Returns dict of common template expansions."""
        vlan = self.vlan
        return dict(
            addr4=vlan.addrs(4),
            addr6=vlan.addrs(6),
            addresses=vlan.addrs(),
            gateways=vlan.gateways_filtered(),
            iface=vlan.iname(),
            mac=vlan.mac,
            metric=vlan.metric,
            mtu=vlan.mtu,
            nets4=vlan.nets(4),
            nets6=vlan.nets(6),
            nets=vlan.nets(),
            vlan=vlan.name,
        )

    def register(self, callbacks):
        self.callbacks.extend(callbacks)

    def generate(self):
        """Returns list/generator of Conffiles.

        To be overriden in subclasses.
        """
        return []

# XXX helper really necessary?
    def _conffile(self, relpath, templates, values, services):
        out = ''.join(self.tmpl.get_template(t).render(**values)
                      for t in templates)
        return Conffile(relpath, out, set(services))


class UntaggedPolicy(NetworkPolicy):

    def generate(self):
        vlan = self.vlan
        v = self.common_values()
        for cb in self.callbacks:
            cb.register_mac(mac=vlan.mac, name=vlan.basename)
        if vlan.bridged:
            v['baseiface'] = vlan.basename
            yield self._conffile(
                'conf.d/net.d/iface.' + vlan.iname(),
                ['iface_untagged_common', 'iface_untagged_bridged'], v,
                ['net.' + vlan.iname(), 'net.' + vlan.basename])
        else:
            yield self._conffile(
                'conf.d/net.d/iface.' + vlan.iname(),
                ['iface_untagged_common', 'iface_untagged_unbridged'], v,
                ['net.' + vlan.iname()])


class TaggedPolicy(NetworkPolicy):

    def generate(self):
        vlan = self.vlan
        name = self.vlan.name
        v = self.common_values()
        mux_iface = v['mux_iface'] = (
            'enx{}'.format(self.vlan.mac).replace(':', ''))
        for cb in self.callbacks:
            cb.register_mac(mac=vlan.mac, name=mux_iface)
            cb.register_mux(mux_iface=mux_iface, vlan=vlan)
        if vlan.bridged:
            v['baseiface'] = vlan.basename
            yield self._conffile(
                'conf.d/net.d/iface.' + vlan.iname(),
                ['iface_untagged_common', 'iface_untagged_bridged'], v,
                {'net.br' + name})
        else:
            yield self._conffile(
                'conf.d/net.d/iface.' + vlan.iname(),
                ['iface_untagged_common', 'iface_untagged_unbridged'], v,
                set())


class TransitPolicy(NetworkPolicy):

    pass


class IPMIPolicy(NetworkPolicy):  # XXX is IPMI tagged or untagged?

    pass
