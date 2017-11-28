from fc.network.main import build_policy, configs
from fc.network.conffile import Conffile


def test_generated_configs(untagged, networkcfg):
    cfg = configs(untagged, networkcfg)
    assert [
        'conf.d/net.d/iface.brfe',
        'conf.d/net.d/iface.brsrv',
        'conf.d/net.d/iface.ethmgm',
        'conf.d/net.d/iface.ethsto',
        'rules.d/70-persistent-net-ethfe.rules',
        'rules.d/70-persistent-net-ethmgm.rules',
        'rules.d/70-persistent-net-ethsrv.rules',
        'rules.d/70-persistent-net-ethsto.rules',
    ] == sorted([c.relpath for c in cfg])


def test_config_mgm_untagged(untagged, networkcfg, netd):
    """Unbrigded."""
    pol = build_policy('mgm', untagged['mgm'], networkcfg)
    exp = Conffile('conf.d/net.d/iface.ethmgm',
                   netd('untagged', 'iface.ethmgm'),
                   set(['net.ethmgm']))
    assert next(pol.generate()).diff(exp) == ""


def test_config_fe_untagged(untagged, networkcfg, netd):
    """Bridged."""
    pol = build_policy('fe', untagged['fe'], networkcfg)
    exp = Conffile('conf.d/net.d/iface.brfe',
                   netd('untagged', 'iface.brfe'),
                   set(['net.ethfe', 'net.brfe']))
    assert next(pol.generate()).diff(exp) == ""


def test_config_srv_untagged(untagged, networkcfg, netd):
    """Test with default values from config file."""
    pol = build_policy('srv', untagged['srv'], networkcfg)
    exp = Conffile('conf.d/net.d/iface.brsrv',
                   netd('untagged', 'iface.brsrv'),
                   set(['net.ethsrv', 'net.brsrv']))
    assert next(pol.generate()).diff(exp) == ""


def test_config_sto_untagged(untagged, networkcfg, netd):
    """Test with default values from config file."""
    pol = build_policy('sto', untagged['sto'], networkcfg)
    exp = Conffile('conf.d/net.d/iface.ethsto',
                   netd('untagged', 'iface.ethsto'),
                   set(['net.ethsto']))
    assert next(pol.generate()).diff(exp) == ""


# XXX test_ipmi
