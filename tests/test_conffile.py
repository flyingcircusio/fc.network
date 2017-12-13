from fc.network.conffile import Conffile, cleanup
import pkg_resources
import pytest
import os.path as p


@pytest.fixture
def brsrv():
    with pkg_resources.resource_stream(
            __name__, 'fixtures/untagged/conf.d/net.d/iface.brsrv') as f:
        return f.read().decode()


def test_rewrite_conffile(brsrv, tmpdir):
    tgt = tmpdir / 'iface.brsrv'
    tgt.write(brsrv)
    c = Conffile('iface.brsrv', brsrv)
    assert c.write(prefix=str(tmpdir)) is False, \
        'should report file as untouched'
    assert brsrv == tgt.read()
    with open(str(tgt), 'r+') as f:
        f.truncate(250)
    c = Conffile('iface.brsrv', brsrv)
    assert c.write(str(tmpdir)) is True, 'should report file as edited'
    assert brsrv == tgt.read()


def test_create_conffile(brsrv, tmpdir):
    c = Conffile('iface.brsrv', brsrv)
    assert c.write(str(tmpdir)) is True, 'should report file as edited'
    assert brsrv == (tmpdir / 'iface.brsrv').read()


def test_create_leading_dir(brsrv, tmpdir):
    c = Conffile('net.d/iface.brsrv', brsrv)
    assert c.write(str(tmpdir)) is True, 'should report file as edited'
    assert brsrv == (tmpdir / 'net.d/iface.brsrv').read()


def test_nodo(tmpdir):
    f = tmpdir / 'iface.test'
    f.write('foo\n')
    c = Conffile(str(f), 'bar\n')
    assert c.write('', do=False) is True, 'should report file as edited'
    assert 'foo\n' == f.read()


def test_cleanup_removes_old_file(tmpdir):
    tmpdir.ensure('iface.new')
    tmpdir.ensure('iface.old')
    assert cleanup(str(tmpdir / 'iface.*'), [str(tmpdir / 'iface.new')],
                   do=False)
    assert p.exists(str(tmpdir / 'iface.old'))

    assert cleanup(str(tmpdir / 'iface.*'), [str(tmpdir / 'iface.new')],
                   do=True)
    assert not p.exists(str(tmpdir / 'iface.old'))
    assert p.exists(str(tmpdir / 'iface.new'))


def test_cleanup_nothing_to_do(tmpdir):
    tmpdir.ensure('iface.0')
    tmpdir.ensure('iface.1')
    assert not cleanup(str(tmpdir / 'iface.*'),
                       [str(tmpdir / 'iface.0'), str(tmpdir / 'iface.1')])
    assert p.exists(str(tmpdir / 'iface.0'))
    assert p.exists(str(tmpdir / 'iface.1'))
