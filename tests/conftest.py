from pkg_resources import resource_stream, resource_filename, resource_string
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
    """ENC interfaces for quimby untagged."""
    with resource_stream(__name__, 'fixtures/untagged/enc/quimby.json') as f:
        return json.loads(f.read().decode('ascii'))['parameters']['interfaces']


@pytest.fixture
def tagged():
    """ENC interfaces for quimby tagged."""
    with resource_stream(__name__, 'fixtures/tagged/enc/quimby.json') as f:
        return json.loads(f.read().decode('ascii'))['parameters']['interfaces']

@pytest.fixture
def networkcfg():
    cp = configparser.ConfigParser()
    cp.read(resource_filename(__name__, 'fixtures/fc-network.cfg'))
    return cp


@pytest.fixture
def netd():
    """Expected result config file."""
    def load(testset, filename):
        return resource_string(__name__, 'fixtures/{}/conf.d/net.d/{}'.format(
            testset, filename)).decode('ascii')
    return load
