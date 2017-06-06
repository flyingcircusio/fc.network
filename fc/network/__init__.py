"""FCIO network configuration utility NG.

This tool reads host configuration data from an ENC JSON dump and
configures networking accordingly. Configuration items include
/etc/conf.d/net.d/iface.*, /etc/udev/rules.d/*, /etc/mactab.
"""
import argparse

from .main import configure


def main():
    a = argparse.ArgumentParser(description=__doc__, epilogue="""
Exit status is 0 if nothing needs to be changed, 2 if something should
be updated, 1 on error.
""")
    a.add_argument('-E', '--enc', metavar='PATH',
                   default='/etc/puppet/enc.json',
                   help='ENC JSON dump (default: %(default)s)')
    a.add_argument('--confroot', metavar='DIR', default='/etc',
                   help='base dir for generated configuration files '
                   '(default: %(default)s)')
    a.add_argument('-n', '--dry-run', default=False, action='store_true',
                   help="don't update files, don't start/stop services")
    a.add_argument('-r', '--restart', default=False, action='store_true',
                   help='restart all services unconditionally')
    args = a.parse_args()
    configure(args.enc, args.confroot, args.dry_run, args.restart)
