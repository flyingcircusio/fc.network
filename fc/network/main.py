"""Flying Circus network configuration utility."""

import glob
import os
import os.path as p


def ensure_udev_rules(ports, rulesd):
    # WIP
    # clean up old Puppet conffiles
    for fn in glob.glob(p.join(rulesd, '70-persistent-net*')):
        os.unlink(fn)


def ensure_mactab(ports, confroot):
    # WIP
    pass


def ensure_confd_netd(ports, confroot):
    # WIP
    pass


def configure(enc, confroot, dry_run, force_restart):
    # WIP
    pass
