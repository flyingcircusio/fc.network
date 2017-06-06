import json
import pkg_resources
import pytest

from fc.network.model import Port
from fc.network.render import render, Ifaces, UdevRules, Mactab


@pytest.fixture(scope='module', params=['untagged', 'tagged', 'transit'])
def render_data(request):
    """Loads ENC inputs and expected conf.d/net.d results."""
    flavour = request.param
    res = {}
    with pkg_resources.resource_stream(
            __name__, 'fixtures/enc/quimby_{}.json'.format(flavour)) as f:
        res['enc'] = json.loads(f.read().decode('ascii'))['parameters']
    with pkg_resources.resource_stream(
            __name__, 'fixtures/conf.d/net.d/quimby_{}'.format(flavour)) as f:
        res['netd'] = f.read().decode('ascii')
    with pkg_resources.resource_stream(
            __name__, 'fixtures/udev/rules.d/quimby_{}'.format(flavour)) as f:
        res['udev'] = f.read().decode('ascii')
    with pkg_resources.resource_stream(
            __name__, 'fixtures/mactab_{}'.format(flavour)) as f:
        res['mactab'] = f.read().decode('ascii')
    res['ports'] = [Port(p) for p in res['enc']['network']]
    return res


def test_iface_rendered(render_data, tmpdir):
    iface = render(Ifaces(), render_data['ports'])
    # dump output into file for ease of debugging
    (tmpdir / 'iface.all').write_text(iface, 'ascii')
    assert render_data['netd'] == iface


def test_render_udev_rules(render_data):
    rules = render(UdevRules(), render_data['ports'])
    assert render_data['udev'] == rules


def test_render_mactab(render_data):
    mactab = render(Mactab(), render_data['ports'])
    assert render_data['mactab'] == mactab
