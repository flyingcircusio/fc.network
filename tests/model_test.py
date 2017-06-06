import ipaddress as ip
import pytest

from fc.network.model import VLAN, Port


def test_lowlevel_name_simple():
    p = Port({'port': 'base0', 'vlans': {'srv': {}}})
    assert p.tagged is False
    assert p.lowlevel_name == 'ethsrv'


def test_lowlevel_name_multiple_vlans():
    p = Port({'port': 'base1', 'vlans': {
        'fe': {'tagged': True, 'vlanid': 2},
        'srv': {'tagged': True, 'vlanid': 3},
    }})
    assert p.tagged is True
    assert p.lowlevel_name == 'ethbase1'


def test_port_name_too_long():
    with pytest.raises(ValueError):
        Port({'port': 'toolong', 'vlans': {}})


def test_port_name_invalid_chars():
    with pytest.raises(ValueError):
        Port({'port': 'ext-1', 'vlans': {}})


def test_cannot_mix_tagged_untagged():
    with pytest.raises(RuntimeError):
        Port({'port': 0, 'vlans': {
            'srv': {'tagged': 3},
            'fe': {'tagged': False},
        }})


def test_addresses():
    v = VLAN('fe', {'networks': {
        '2a02:238:f030:1c1::/64': ['2a02:238:f030:1c1::37'],
        '172.20.1.0/24': ['172.20.1.91']
    }})
    assert [
        ip.ip_interface('172.20.1.91/24'),
        ip.ip_interface('2a02:238:f030:1c1::37/64'),
    ] == list(v.addresses)


def test_nets():
    v = VLAN('fe', {'networks': {
        '2a02:238:f030:1c1::/64': [],
        '172.20.1.0/24': [],
        '10.45.0.0/16': [],
    }})
    assert [
        ip.ip_network('10.45.0.0/16'),
        ip.ip_network('172.20.1.0/24'),
        ip.ip_network('2a02:238:f030:1c1::/64'),
    ] == list(v.nets)


def test_phyname_ifname_collision():
    with pytest.raises(ValueError):
        Port({'port': 'fe', 'vlans': {'fe': {'tagged': True, 'vlanid': 2}}})


def test_must_specify_vlanid_if_tagged():
    with pytest.raises(RuntimeError):
        Port({'port': 'mb', 'vlans': {'fe': {'tagged': True}}})


def test_conffile_name():
    assert 'iface.ethfe' == Port(
        {'port': 'fe', 'vlans': {'fe': {}}}).conffile_name
    assert 'iface.eth0' == Port(
        {'port': '0', 'vlans': {'fe': {'tagged': True, 'vlanid': 2}}}
    ).conffile_name


def test_mtu_max():
    assert 9000 == Port({
        'port': 0, 'vlans': {'fe': {'mtu': 1600}, 'sto': {'mtu': 9000}}
    }).mtu_max
    assert 1280 == Port({'port': 0, 'vlans': {'fe': {'mtu': 1280}}}).mtu_max
    assert 1500 == Port({'port': 0, 'vlans': {}}).mtu_max

# TODO cannot attach bridge to a multiplexed lowlevel interface if tag
# interfaces are also attached
