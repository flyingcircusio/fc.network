import click
import functools
import glob
import os
import os.path as p


def running_services():
    return set()


def enabled_services():
    return set()


def disable(services, do=True):
    click.echo('Disabling services: {}'.format(', '.join(services)))
    return bool(services)


def enable(services, do=True):
    click.echo('Enabling services: {}'.format(', '.join(services)))
    return bool(services)


def stop(services, do=True):
    click.echo('Stopping services: {}'.format(', '.join(services)))
    return bool(services)


def start(services, do=True):
    click.echo('Starting services: {}'.format(', '.join(services)))
    return bool(services)


def restart(services, do=True):
    click.echo('Restarting services: {}'.format(', '.join(services)))
    return bool(services)


def cleanup(configs, prefix, do=True):
    present = set(glob.glob(p.join(prefix, 'conf.d/net.d/iface.*')))
    desired = set(c.path(prefix) for c in configs)
    remove = present - desired
    if not remove:
        return False
    if not do:
        click.echo('Would remove superfluous config files: {}'.
                   format(', '.join(remove)))
        return True
    click.echo('Removing superfluous config files: {}'.
               format(', '.join(remove)))
    for f in remove:
        os.unlink(f)
    return True


def apply_configs(configs, do_edit, do_restart, prefix="/etc"):
    changed = False
    enabled = enabled_services()
    running = running_services()
    desired = functools.reduce(set.union, (c.svc for c in configs))
    changed |= disable(enabled - desired, do_restart)
    changed |= stop(running - desired, do_restart)
    need_restart = set()
    for config in configs:
        if config.apply(prefix, do_edit):
            need_restart.update(config.svc)
            changed = True
    changed |= cleanup(configs, prefix, do_edit)
    changed |= enable(desired - enabled, do_restart)
    changed |= restart(need_restart & running, do_restart)
    changed |= start(desired - running, do_restart)
    return changed
