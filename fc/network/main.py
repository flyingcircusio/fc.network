"""Flying Circus network configuration utility."""

import glob
import json
import os
import os.path as p

from .model import Port
from .render import render, Ifaces, UdevRules, Mactab


def ensure_udev_rules(ports, rulesd):
    #write_conf(render(UdevRules(), ports),
               #p.join(rulesd, '71-persistent-net.rules'))
    # clean up old Puppet conffiles
    for fn in glob.glob(p.join(rulesd, '70-persistent-net*')):
        os.unlink(fn)


def ensure_mactab(ports, confroot):
    #write_conf(render(Mactab(), ports), p.join(confroot, 'mactab'))
    pass


def ensure_confd_netd(ports, confroot):
    for port in ports:
        conf = render(Ifaces(), [port])
        fn = p.join(confroot, 'conf.d', 'net.d', port.conffile_name)
        # XXX write_conf(conf, fn)


def configure(enc, confroot, dry_run, force_restart):
    with open(enc) as f:
        params = json.load(f)['parameters']
    config = [Port(net) for net in params['network']]
