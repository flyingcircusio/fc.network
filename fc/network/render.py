import jinja2

TMPL = jinja2.Environment(
    line_statement_prefix='%%', keep_trailing_newline=True)

MARKER = "# Managed by configure-network. Don't edit.\n"


class Ifaces:

    def tagged_prelude(self, port):
        vlans = {v.vlanid: v.bridgebase_name for k, v in port.vlans.items()
                 if v.mode != 'bmc' and v.tagged and v.vlanid}
        yield from TMPL.from_string("""\
config_{{phyname}}="null"
mtu_{{phyname}}={{mtu}}
vlans_{{phyname}}="{{ids}}"
%% for id, vname in vlans
vlan{{id}}_name="{{vname}}"
%% endfor
""").generate(phyname=port.lowlevel_name, vlans=sorted(vlans.items()),
              ids=' '.join(str(i) for i in sorted(vlans.keys())),
              mtu=port.mtu_max)

    def static_vlan(self, vlan):
        yield from TMPL.from_string("""\
%% if bridged
config_{{basedev}}="null"
bridge_{{iface}}="{{basedev}}"
%% endif
config_{{iface}}="
%% for addr in addrs
    {{addr}}
%% endfor
"
routes_{{iface}}="
%% for net in nets
    {{net}} table {{name}}
%% endfor
%% for gw in gateways
    default via {{gw}} table {{name}}
    default via {{gw}}
%% endfor
"
rules_{{iface}}="
%% for addr in addrs if addr.version == 4
    from {{addr}} table {{name}} priority {{metric}}
%% endfor
%% for net in nets if net.version == 4
    to {{net}} table {{name}} priority {{metric}}
%% endfor
"
rules6_{{iface}}="
%% for addr in addrs if addr.version == 6
    from {{addr}} table {{name}} priority {{metric}}
%% endfor
%% for net in nets if net.version == 6
    to {{net}} table {{name}} priority {{metric}}
%% endfor
"
metric_{{iface}}={{metric}}
mtu_{{basedev}}={{mtu}}
dad_timeout_{{iface}}=10
""").generate(iface=vlan.interface_name, basedev=vlan.bridgebase_name,
              name=vlan.name, metric=vlan.metric, mtu=vlan.mtu,
              bridged=vlan.bridged,
              addrs=list(vlan.addresses), nets=list(vlan.nets),
              gateways=[gw for gw in vlan.gateways
                        if any(gw in n for n in vlan.used_nets)])

    def dhcp_vlan(self, vlan):
        yield from TMPL.from_string("""\
%% if bridged
config_{{basedev}}="null"
bridge_{{iface}}="{{basedev}}"
%% endif
config_{{iface}}="dhcp"
metric_{{iface}}={{metric}}
mtu_{{basedev}}={{mtu}}
dad_timeout_{{iface}}=10
""").generate(iface=vlan.interface_name, basedev=vlan.bridgebase_name,
              metric=vlan.metric, mtu=vlan.mtu, bridged=vlan.bridged)

    def null_vlan(self, vlan):
        yield from TMPL.from_string("""\
%% if bridged
config_{{basedev}}="null"
bridge_{{iface}}="{{basedev}}"
%% endif
config_{{iface}}="null"
""").generate(iface=vlan.interface_name, basedev=vlan.bridgebase_name,
              bridged=vlan.bridged)

    def render_item(self, port):
        yield from TMPL.from_string("""
# === Port "{{name}}" {% if mac %}({{mac}}) {% endif %}===
""").generate(name=port.name, mac=port.mac)
        if port.tagged:
            yield from self.tagged_prelude(port)
        for vname, vlan in sorted(
                port.vlans.items(),
                key=lambda item: (item[1].vlanid, item[1].name)):
            yield '\n# === VLAN "{}" ===\n'.format(vname)
            if vlan.mode == 'static':
                yield from self.static_vlan(vlan)
            elif vlan.mode == 'dhcp':
                yield from self.dhcp_vlan(vlan)
            elif vlan.mode == 'bmc':
                yield '# see /etc/ipmi/bmc-config.sh\n'
            elif vlan.mode == 'null':
                yield from self.null_vlan(vlan)
            else:
                raise RuntimeError(
                    "don't know how to generate config for {} mode".format(
                        vlan.mode),
                    vlan.bridgebase_name)


class UdevRules:

    def render_item(self, port):
        if not port.mac:
            return
        yield from TMPL.from_string("""\
SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="{{mac}}", \
ATTR{type}=="1", KERNEL=="eth*", NAME="{{phyname}}"
""").generate(mac=port.mac, phyname=port.lowlevel_name)


class Mactab:

    def render_item(self, port):
        if not port.mac:
            return
        yield from TMPL.from_string("""\
{{phyname}}\t{{mac}}
""").generate(mac=port.mac, phyname=port.lowlevel_name)


def render(renderer, items):
    res = [MARKER]
    for i in items:
        res += renderer.render_item(i)
    return ''.join(res)
