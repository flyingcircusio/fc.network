"""Flying Circus network configuration utility."""

from fc.network.policy import NetworkPolicy
from fc.network.aux import Demux, Mactab, Udev
from fc.network.activation import apply_configs
import click
import configparser
import json


class VLAN():

    def __init__(self, name, enc, staticcfg):
        self.name = name
        self.network_policy = enc.get('network_policy') or 'puppet'
        self.mac = enc['mac'].lower() or '00:00:00:00:00:00'
        self.networks = enc.get('networks', {})
        self.gateways = enc.get('gateways', {})
        self.staticcfg = staticcfg

    def __str__(self):
        return 'VLAN({})'.format(self.__dict__)

    @property
    def bridged(self):
        return self.staticcfg.getboolean('bridged')

    @property
    def mtu(self):
        return self.staticcfg.getint('mtu')

    @property
    def vlan_id(self):
        return self.staticcfg.getint('vlan_id')

    @property
    def metric(self):
        return self.staticcfg.getint('metric')


def build_policy(name, enc_ifaces, networkcfg):
    """Returns network policies + VLANS for enc interfaces."""
    static = (networkcfg[name] if name in networkcfg
              else networkcfg[networkcfg.default_section])
    vlan = VLAN(name, enc_ifaces[name], static)
    return NetworkPolicy.for_vlan(vlan)


def configs(enc_ifaces, networkcfg):
    configs = []
    demux = Demux()
    mactab = Mactab()
    udev = Udev()

    for name in enc_ifaces:
        policy = build_policy(name, enc_ifaces, networkcfg)
        if not policy:
            continue
        configs.extend(policy.generate(demux=demux, mactab=mactab, udev=udev))
        configs.extend(demux.generate())
        configs.extend(mactab.generate())
        configs.extend(udev.generate())

    return configs


@click.command()
@click.option("--dry-run", "-n", is_flag=True,
              help="Don't edit config files and don't start services.")
@click.option("--restart/--no-restart", "-R/-r", default=True,
              help="Start or stop services (default: yes unless dry run).")
@click.help_option("-h", "--help")
@click.argument("enc", type=click.File('r'))
@click.argument("networkcfg", type=click.File('r'))
def main(dry_run, restart, enc, networkcfg):
    cp = configparser.ConfigParser()
    cfg = configs(json.load(enc)['parameters']['interfaces'],
                  cp.read_file(networkcfg))
    apply_configs(cfg, not dry_run, not dry_run and restart)
