from fc.network.main import build_policy, configs
from fc.network.conffile import Conffile
from fc.network.aux import Mactab, Udev


def test_generated_configs(untagged, networkcfg):
    cfg = configs(untagged['parameters']['interfaces'], networkcfg)
    assert [
        'conf.d/net.d/iface.brfe',
        'conf.d/net.d/iface.brsrv',
        'conf.d/net.d/iface.ethipmi',
        'conf.d/net.d/iface.ethmgm',
        'conf.d/net.d/iface.ethsto',
    ] == sorted([c.relpath for c in cfg])


def test_config_mgm_untagged(untagged, networkcfg):
    pol = build_policy('mgm', untagged['parameters']['interfaces'], networkcfg)
    exp = Conffile('conf.d/net.d/iface.ethmgm', """\
# Managed by fc.network. Don't edit manually.
# === VLAN mgm (b8:ac:6f:15:dd:08) ===
config_ethmgm="
    172.20.1.90/24
    2a02:238:f030:1c1::1075/64
"
routes_ethmgm="
    default via 172.20.1.1
    default via 2a02:238:f030:1c1::1
"
metric_ethmgm=2000
mtu_ethmgm=1500
dad_timeout_ethmgm=10
""", set(['net.ethmgm']))
    assert next(pol.generate(mactab=Mactab(), udev=Udev())).diff(exp) == ""


def test_config_fe_untagged(untagged, networkcfg):
    pol = build_policy('fe', untagged['parameters']['interfaces'], networkcfg)
    exp = Conffile('conf.d/net.d/iface.brfe', """\
# Managed by fc.network. Don't edit manually.
# === VLAN fe (b8:ac:6f:15:dd:0c) ===
config_ethfe="null"
bridge_brfe="ethfe"
config_brfe="
    172.20.2.38/25
    2a02:238:f030:1c2::106d/64
    2a02:238:f030:1c2::53/64
"
routes_brfe="
    default via 172.20.2.1
    default via 2a02:238:f030:1c2::1
"
metric_brfe=900
mtu_ethfe=1500
dad_timeout_brfe=10
""", set(['net.ethfe', 'net.brfe']))
    assert next(pol.generate(mactab=Mactab(), udev=Udev())).diff(exp) == ""


# XXX test_ipmi
