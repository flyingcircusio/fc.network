from fc.network.main import build_policy, configs
from fc.network.conffile import Conffile
from fc.network.aux import Mactab, Udev


def test_generated_configs(untagged, networkcfg):
    cfg = configs(untagged, networkcfg)
    assert [
        'conf.d/net.d/iface.brfe',
        'conf.d/net.d/iface.brsrv',
        'conf.d/net.d/iface.ethipmi',
        'conf.d/net.d/iface.ethmgm',
        'conf.d/net.d/iface.ethsto',
    ] == sorted([c.relpath for c in cfg])


def test_config_mgm_untagged(untagged, networkcfg, netd):
    pol = build_policy('mgm', untagged['mgm'], networkcfg)
    exp = Conffile('conf.d/net.d/iface.ethmgm',
                   netd('untagged', 'iface.ethmgm'),
                   set(['net.ethmgm']))
    assert next(pol.generate(mactab=Mactab(), udev=Udev())).diff(exp) == ""


def test_config_fe_untagged(untagged, networkcfg, netd):
    pol = build_policy('fe', untagged['fe'], networkcfg)
    exp = Conffile('conf.d/net.d/iface.brfe',
                   netd('untagged', 'iface.brfe'),
                   set(['net.ethfe', 'net.brfe']))
    assert next(pol.generate(mactab=Mactab(), udev=Udev())).diff(exp) == ""


# XXX test_ipmi
