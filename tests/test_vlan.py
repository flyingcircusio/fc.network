from fc.network.vlan import VLAN


def test_addrs(untagged, networkcfg):
    vlan = VLAN('fe', untagged['fe'], networkcfg)
    assert [
        '172.20.2.38/25',
        '2a02:238:f030:1c2::106d/64',
        '2a02:238:f030:1c2::53/64',
    ] == [str(a) for a in vlan.addrs()]
    assert [
        '172.20.2.38/25',
    ] == [str(a) for a in vlan.addrs(4)]
    assert [
        '2a02:238:f030:1c2::106d/64',
        '2a02:238:f030:1c2::53/64',
    ] == [str(a) for a in vlan.addrs(6)]


def test_nets(untagged, networkcfg):
    vlan = VLAN('fe', untagged['fe'], networkcfg)
    assert [
        '10.2.3.0/24',
        '172.20.2.0/25',
        '2a02:238:f030:1c2::/64',
    ] == [str(n) for n in vlan.nets()]
    assert [
        '10.2.3.0/24',
        '172.20.2.0/25',
    ] == [str(n) for n in vlan.nets(4)]
    assert [
        '2a02:238:f030:1c2::/64',
    ] == [str(n) for n in vlan.nets(6)]
