from fc.network.main import parse_interfaces, UntaggedPolicy, IPMIPolicy
from pkg_resources import resource_stream, resource_filename
import configparser
import json
import pytest


@pytest.fixture(scope='module', params=['untagged', 'tagged', 'transit'])
def enc(request):
    """Loads ENC inputs."""
    variant = request.param
    with resource_stream(
            __name__, 'fixtures/{}/enc/quimby.json'.format(variant)) as f:
        return json.loads(f.read().decode('ascii'))


@pytest.fixture
def untagged():
    with resource_stream(__name__, 'fixtures/untagged/enc/quimby.json') as f:
        return json.loads(f.read().decode('ascii'))


@pytest.fixture
def networkcfg():
    cp = configparser.ConfigParser()
    cp.read(resource_filename(__name__, 'fixtures/fc-network.cfg'))
    return cp


def test_parse_untagged(untagged, networkcfg):
    ifaces = parse_interfaces(untagged['parameters']['interfaces'], networkcfg)
    assert sorted(ifaces.keys()) == [
        'b8:ac:6f:15:dd:08',
        'b8:ac:6f:15:dd:0a',
        'b8:ac:6f:15:dd:0c',
        'b8:ac:6f:15:dd:0e',
        'b8:ac:6f:15:dd:10',
    ]
    for policy in ifaces.values():
        assert len(policy.vlans) == 1
    assert type(ifaces['b8:ac:6f:15:dd:0c']) == UntaggedPolicy
    assert type(ifaces['b8:ac:6f:15:dd:10']) == IPMIPolicy


def test_disallow_different_policies_on_same_iface(untagged, networkcfg):
    ifaces = untagged['parameters']['interfaces']
    ifaces['ipmi']['mac'] = ifaces['mgm']['mac']
    with pytest.raises(RuntimeError):
        parse_interfaces(ifaces, networkcfg)


def test_disallow_several_untagged_vlans_on_one_iface(untagged, networkcfg):
    ifaces = untagged['parameters']['interfaces']
    ifaces['srv']['mac'] = ifaces['mgm']['mac']
    with pytest.raises(RuntimeError):
        parse_interfaces(ifaces, networkcfg)
