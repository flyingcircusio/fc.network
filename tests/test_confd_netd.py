from fc.network.main import instantiate
from fc.network.policy import NetworkPolicy
from fc.network.conffile import Conffile
import pytest


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


def test_config_puppet(puppet, networkcfg):
    with pytest.raises(RuntimeError):
        NetworkPolicy.build('srv', puppet['srv'], networkcfg)


def test_iface_config_tagged(tagged, networkcfg, netd):
    ifaces_activation = instantiate(tagged, networkcfg)

    exp_fe = Conffile('conf.d/net.d/iface.brfe',
                      netd('tagged', 'iface.brfe'),
                      {'net.brfe'})
    assert ifaces_activation.configs[0].diff(exp_fe) == ""
    assert ifaces_activation.configs[0].svc == exp_fe.svc

    exp_sto = Conffile('conf.d/net.d/iface.ethsto',
                       netd('tagged', 'iface.ethsto'),
                       set())
    assert ifaces_activation.configs[3].diff(exp_sto) == ""
    assert ifaces_activation.configs[3].svc == exp_sto.svc


def test_demux_config_tagged(tagged, networkcfg, netd):
    ifaces_activation = instantiate(tagged, networkcfg)
    exp = Conffile('conf.d/net.d/iface.enxb8ac6f15dd0c',
                   netd('tagged', 'iface.enxb8ac6f15dd0c'),
                   {'net.enxb8ac6f15dd0c'})
    assert ifaces_activation.configs[-2].diff(exp) == ""
    assert ifaces_activation.configs[-2].svc == exp.svc


def test_mactab_udev_tagged(tagged, networkcfg, fixstr):
    mactab_activation = instantiate(tagged, networkcfg).inner
    exp = Conffile('mactab', fixstr('tagged', 'mactab'), set())
    assert mactab_activation.configs[0].diff(exp) == ""

    udev_activation = mactab_activation.inner
    exp = Conffile('udev/rules.d/70-network.rules',
                   fixstr('tagged', 'udev/rules.d/70-quimby.rules'),
                   set())
    assert udev_activation.configs[0].diff(exp) == ""
