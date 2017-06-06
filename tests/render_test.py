import json
import pkg_resources
import pytest

from fc.network.model import Port
from fc.network.render import render, Ifaces, UdevRules, Mactab


@pytest.fixture
def quimby_untagged():
    with pkg_resources.resource_stream(
            __name__, 'fixtures/enc/quimby_untagged.json') as f:
        enc = json.loads(f.read().decode('ascii'))
    return [Port(p) for p in enc['parameters']['network']]


@pytest.fixture
def quimby_tagged():
    with pkg_resources.resource_stream(
            __name__, 'fixtures/enc/quimby_tagged.json') as f:
        enc = json.loads(f.read().decode('ascii'))
    return [Port(p) for p in enc['parameters']['network']]


def test_iface_untagged(quimby_untagged):
    conf = render(Ifaces(), quimby_untagged)
    with pkg_resources.resource_stream(
            __name__, 'fixtures/conf.d/net.d/quimby_untagged') as f:
        assert f.read().decode('ascii') == conf


def test_render_udev_rules(quimby_untagged):
    rules = render(UdevRules(), quimby_untagged)
    with pkg_resources.resource_stream(
            __name__, 'fixtures/udev/rules.d/quimby') as f:
        assert f.read().decode('ascii') == rules


def test_render_mactab(quimby_untagged):
    conf = render(Mactab(), quimby_untagged)
    with pkg_resources.resource_stream(
            __name__, 'fixtures/mactab_quimby') as f:
        assert f.read().decode('ascii') == conf


def test_iface_tagged(quimby_tagged):
    conf = render(Ifaces(), quimby_tagged)
    with pkg_resources.resource_stream(
            __name__, 'fixtures/conf.d/net.d/quimby_tagged') as f:
        assert f.read().decode('ascii') == conf


def test_iface_dhcp():
    port = Port({'port': 'mb1', 'mac': '00:11:22:33:44:55', 'vlans': {'srv': {
        'mode': 'dhcp', 'bridged': True, 'metric': 1100}}})
    conf = render(Ifaces(), [port])
    with pkg_resources.resource_stream(
            __name__, 'fixtures/conf.d/net.d/quimby_srv_dhcp') as f:
        assert f.read().decode('ascii') == conf
