import pytest

from pkg_resources import resource_stream, resource_filename
import configparser
import json


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
