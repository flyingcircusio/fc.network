from fc.network.conffile import Conffile
from fc.network.activation import OpenRC
import os
import pytest


@pytest.fixture
def rl(tmpdir):
    return (tmpdir / 'runlevels' / 'default').ensure(dir=True)


@pytest.fixture
def initd(tmpdir):
    return (tmpdir / 'init.d').ensure(dir=True)


def test_cleanup_confd(tmpdir):
    tmpdir.mkdir('conf.d')
    p = tmpdir.mkdir('conf.d', 'net.d')
    p.ensure('iface.new')
    p.ensure('iface.old')
    c = Conffile('conf.d/net.d/iface.new', '')
    OpenRC(prefix=str(tmpdir)).cleanup([c])
    assert os.path.exists(str(p / 'iface.new'))
    assert not os.path.exists(str(p / 'iface.old'))


def test_running(monkeypatch):
    def mock_check_output(*args, **kw):
        return (b"""\
 * Caching service dependencies ...                          [ ok ]
Runlevel: default
 ip6tables                                            [  started  ]
 iptables                                             [  started  ]
 net.lo                                               [  started  ]
 net.brfe                                             [  stopped  ]
 net.brsrv                                            [  started  ]
 net.ethfe                                            [  started  ]
 net.ethmgm                                           [  crashed  ]
 net.ethsrv                                           [  starting ]
 net.ethsto                                           [  started  ]
 consul                                               [  started  ]
 haveged                                              [  started  ]
 named                                                [  started  ]
""")
    monkeypatch.setattr('subprocess.check_output', mock_check_output)
    assert set(['net.brsrv', 'net.ethfe', 'net.ethsto']
               ) == OpenRC().running()


def test_enabled(rl, initd, tmpdir):
    for svc in ['lvm.vgvm0', 'named', 'net.brfe', 'net.ethfe', 'net.ethsto',
                'net.lo', 'netmount', 'nfsmount', 'nginx']:
        (initd / svc).ensure()
        (rl / svc).mksymlinkto(initd / svc)
    # dangling symlink
    (rl / 'net.brsrv').mksymlinkto(initd / 'net.brsrv')
    # stray file
    (rl / 'net.ethstb').ensure()
    assert set(['net.brfe', 'net.ethfe', 'net.ethsto']
               ) == OpenRC(prefix=str(tmpdir)).enabled()


def test_disable(rl, initd, tmpdir):
    (initd / 'net.lo').ensure()
    (initd / 'net.ethfe').mksymlinkto('net.lo')
    (rl / 'net.ethfe').ensure()
    (initd / 'net.ethsrv').mksymlinkto('net.lo')
    (rl / 'net.ethsrv').ensure()
    # present
    assert OpenRC(prefix=str(tmpdir)).disable(['net.ethfe'])
    assert not (initd / 'net.ethfe').check()
    assert not (rl / 'net.ethfe').check()
    # not present
    assert not OpenRC(prefix=str(tmpdir)).disable(['net.ethsto'])
    assert not (initd / 'net.ethsto').check()
    assert not (rl / 'net.ethsto').check()
    # present, no-do
    assert OpenRC(prefix=str(tmpdir), do=False).disable(['net.ethsrv'])
    assert (initd / 'net.ethsrv').check()
    assert (rl / 'net.ethsrv').check()
    # not present, no-do
    assert not OpenRC(prefix=str(tmpdir), do=False).disable(['net.ethstb'])


def test_enable(rl, initd, tmpdir):
    (initd / 'net.lo').ensure()
    (initd / 'net.ethfe').mksymlinkto('net.lo')
    (rl / 'net.ethfe').mksymlinkto(initd / 'net.ethfe')
    # present
    assert not OpenRC(prefix=str(tmpdir)).enable(['net.ethfe'])
    assert (initd / 'net.ethfe').check()
    assert (rl / 'net.ethfe').check()
    # not present
    assert OpenRC(prefix=str(tmpdir)).enable(['net.ethsto'])
    assert (initd / 'net.ethsto').check()
    assert (rl / 'net.ethsto').check()
    # present, no-do
    assert not OpenRC(prefix=str(tmpdir), do=False).enable(['net.ethfe'])
    assert (initd / 'net.ethfe').check()
    assert (rl / 'net.ethfe').check()
    # not present, no-do
    assert OpenRC(prefix=str(tmpdir), do=False).enable(['net.ethstb'])
    assert not (initd / 'net.ethsrv').check()
    assert not (rl / 'net.ethsrv').check()
