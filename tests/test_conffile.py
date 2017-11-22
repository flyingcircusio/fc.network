from fc.network.conffile import Conffile
import pkg_resources
import pytest


@pytest.fixture
def brsrv():
    with pkg_resources.resource_stream(
            __name__, 'fixtures/untagged/conf.d/net.d/iface.brsrv') as f:
        return f.read().decode()


def test_rewrite_conffile(brsrv, tmpdir):
    tgt = tmpdir / 'iface.brsrv'
    tgt.write(brsrv)
    c = Conffile('iface.brsrv', brsrv)
    assert c.apply(prefix=str(tmpdir)) is False, \
        'should report file as untouched'
    assert brsrv == tgt.read()
    with open(str(tgt), 'r+') as f:
        f.truncate(250)
    c = Conffile('iface.brsrv', brsrv)
    assert c.apply(str(tmpdir)) is True, 'should report file as edited'
    assert brsrv == tgt.read()


def test_create_conffile(brsrv, tmpdir):
    c = Conffile('iface.brsrv', brsrv)
    assert c.apply(str(tmpdir)) is True, 'should report file as edited'
    assert brsrv == (tmpdir / 'iface.brsrv').read()


def test_create_leading_dir(brsrv, tmpdir):
    c = Conffile('net.d/iface.brsrv', brsrv)
    assert c.apply(str(tmpdir)) is True, 'should report file as edited'
    assert brsrv == (tmpdir / 'net.d/iface.brsrv').read()


def test_nodo(tmpdir):
    f = tmpdir / 'iface.test'
    f.write('foo\n')
    c = Conffile(str(f), 'bar\n')
    assert c.apply('', do=False) is True, 'should report file as edited'
    assert 'foo\n' == f.read()
