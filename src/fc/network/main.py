"""Flying Circus network configuration utility."""

from .activation import apply_configs
from .aux import Udev
from .policy import NetworkPolicy
from .vlan import VLAN
import click
import configparser
import json
import sys


def build_policy(name, enc, networkcfg):
    """Returns network policies + VLANS for enc interfaces."""
    static = (networkcfg[name] if name in networkcfg
              else networkcfg[networkcfg.default_section])
    vlan = VLAN(name, enc, static)
    return NetworkPolicy.for_vlan(vlan)


def configs(enc_ifaces, networkcfg):
    aux_configs = [Udev()]
    configs = []
    for name, enc in enc_ifaces.items():
        policy = build_policy(name, enc, networkcfg)
        policy.register(aux_configs)
        if not policy:
            continue
        configs.extend(policy.generate())
    for aux in aux_configs:
        configs.extend(aux.generate())
    return configs


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
    cfg = configs(json.load(enc)['parameters']['interfaces'], cp)
    changed = apply_configs(cfg, prefix=prefix, do_edit=edit,
                            do_restart=edit and restart)
    if changed:
        sys.exit(3)
