"""Flying Circus network configuration utility."""

from .activation import IfacesActivation, matryoshka
from .aux import Udev, Mactab, Demux, UdevActivation, MactabActivation
from .policy import NetworkPolicy
import click
import configparser
import json
import sys


def instantiate(enc_ifaces, networkcfg):
    mactab = Mactab()
    udev = Udev()
    demux = Demux()
    policies = []
    for name, enc in enc_ifaces.items():
        policy = NetworkPolicy.build(name, enc, networkcfg)
        policy.register([mactab, udev, demux])
        policies.append(policy)

    # NetworkPolicy.generate() must be called first to trigger callbacks
    iface_configs = []
    for p in policies:
        iface_configs.extend(p.generate())
    iface_configs.extend(demux.generate())

    return matryoshka([
        UdevActivation(udev.generate()),
        MactabActivation(mactab.generate()),
        IfacesActivation(iface_configs),
    ])


@click.command()
@click.option("--edit/--no-edit", "-e/-n", default=True, show_default=True,
              help="Don't edit config files and don't start services.")
@click.option("--restart/--no-restart", "-R/-r", default=True,
              help="Start or stop services.  [default: yes unless no-edit]")
@click.option("--prefix", default='/etc', help='Root for config file editing.',
              show_default=True, type=click.Path(file_okay=False))
@click.help_option("-h", "--help")
@click.argument("enc", type=click.File('r'))
@click.argument("networkcfg", type=click.File('r'))
def main(edit, restart, enc, networkcfg, prefix):
    cp = configparser.ConfigParser()
    cp.read_file(networkcfg)
    activation = instantiate(json.load(enc)['parameters']['interfaces'], cp)
    changed = activation.activate(prefix, edit, restart)
    # XXX clean up: iface, udev
    if changed:
        sys.exit(3)
