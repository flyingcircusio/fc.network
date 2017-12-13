from fc.network.main import instantiate
from fc.network.policy import NetworkPolicy
from fc.network.conffile import Conffile


def test_config_mgm_untagged(untagged, networkcfg, netd):
    """Unbrigded."""
    pol = NetworkPolicy.build('mgm', untagged['mgm'], networkcfg)
    exp = Conffile('conf.d/net.d/iface.ethmgm',
                   netd('untagged', 'iface.ethmgm'),
                   set(['net.ethmgm']))
    assert next(pol.generate()).diff(exp) == ""


def test_config_fe_untagged(untagged, networkcfg, netd):
    """Bridged."""
    pol = NetworkPolicy.build('fe', untagged['fe'], networkcfg)
    exp = Conffile('conf.d/net.d/iface.brfe',
                   netd('untagged', 'iface.brfe'),
                   set(['net.ethfe', 'net.brfe']))
    assert next(pol.generate()).diff(exp) == ""


def test_config_srv_untagged(untagged, networkcfg, netd):
    """Test with default values from config file."""
    pol = NetworkPolicy.build('srv', untagged['srv'], networkcfg)
    exp = Conffile('conf.d/net.d/iface.brsrv',
                   netd('untagged', 'iface.brsrv'),
                   set(['net.ethsrv', 'net.brsrv']))
    assert next(pol.generate()).diff(exp) == ""


def test_config_sto_untagged(untagged, networkcfg, netd):
    """Test with default values from config file."""
    pol = NetworkPolicy.build('sto', untagged['sto'], networkcfg)
    exp = Conffile('conf.d/net.d/iface.ethsto',
                   netd('untagged', 'iface.ethsto'),
                   set(['net.ethsto']))
    assert next(pol.generate()).diff(exp) == ""


def test_config_tagged(tagged, networkcfg, netd):
    activations = instantiate(tagged, networkcfg)
    ifaces_act = activations.pop()


# XXX test_ipmi
