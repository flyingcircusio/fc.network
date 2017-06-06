import json
import pkg_resources
import pytest

from fc.network.model import Port
from fc.network.render import Ifaces

@pytest.fixture
def quimby_untagged():
    with pkg_resources.resource_stream(
            __name__, 'fixtures/enc/quimby_untagged.json') as f:
        return json.loads(f.read().decode('ascii'))['parameters']


def test_iface_rendered(quimby_untagged, tmpdir):
    ports = [Port(p) for p in quimby_untagged['network']]
    conf = Ifaces().render(ports)
    with pkg_resources.resource_stream(
            __name__, 'fixtures/conf.d/net.d/quimby_untagged') as f:
        assert f.read().decode('ascii') == conf
