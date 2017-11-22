from fc.network.conffile import Conffile
from fc.network import activation
import os


def test_cleanup_confd(tmpdir):
    tmpdir.mkdir('conf.d')
    p = tmpdir.mkdir('conf.d', 'net.d')
    p.ensure('iface.new')
    p.ensure('iface.old')
    c = Conffile('conf.d/net.d/iface.new', '')
    activation.cleanup([c], str(tmpdir))
    assert os.path.exists(str(p / 'iface.new'))
    assert not os.path.exists(str(p / 'iface.old'))
