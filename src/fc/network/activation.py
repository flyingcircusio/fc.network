import click
import functools
import glob
import os
import os.path as p
import re
import subprocess


class OpenRC:

    def __init__(self, runlevel='default', prefix='/etc', do=True):
        self.runlevel = runlevel
        self.prefix = prefix
        self.rl = p.join(prefix, 'runlevels', runlevel)
        self.initd = p.join(prefix, 'init.d')
        self.do = do
        self.changed = False

    def echo(self, *args, **kw):
        if not self.do:
            click.secho("NO-DO: ", nl=False, fg='yellow')
        click.secho(*args, **kw)

    R_STARTED = re.compile(r'^\s*(\S+)\s+\[\s+started\s+\]$')

    def running(self, filter='net.'):
        res = set()
        for line in subprocess.check_output(
                ['rc-status', self.runlevel]).decode('ascii').splitlines():
            m = self.R_STARTED.match(line)
            if m:
                svc = m.group(1)
                if svc.startswith(filter) and svc != 'net.lo':
                    res.add(m.group(1))
        return res

    def enabled(self, filter='net.'):
        res = set()
        for cand in os.listdir(self.rl):
            if cand.startswith(filter) and cand != 'net.lo':
                path = p.join(self.rl, cand)
                if p.islink(path) and p.exists(path):
                    res.add(cand)
        return res

    def _remove(self, file):
        """Returns True if file (has been|would have been) removed."""
        if self.do:
            try:
                os.unlink(file)
                return True
            except OSError as e:
                self.echo(str(e), fg='red')
                return False
        return p.exists(file)

    def disable(self, services):
        changed = False
        for svc in services:
            self.echo('Disabling service: {}'.format(svc))
            changed |= self._remove(p.join(self.rl, svc))
            changed |= self._remove(p.join(self.initd, svc))
        return changed

    def _symlink(self, tgt, file):
        if self.do:
            try:
                os.symlink(tgt, file)
                return True
            except (OSError, FileExistsError) as e:
                self.echo(str(e), fg='red')
                return False
        return not p.exists(file)

    def enable(self, services):
        changed = False
        for svc in services:
            init = p.join(self.initd, svc)
            self.echo('Enabling service: {}'.format(svc))
            changed |= self._symlink('net.lo', init)
            changed |= self._symlink(init, p.join(self.rl, svc))
        return changed

    def stop(self, services):
        self.echo('Stopping services: {}'.format(', '.join(services)))
        return bool(services)

    def start(self, services):
        self.echo('Starting services: {}'.format(', '.join(services)))
        return bool(services)

    def restart(self, services):
        self.echo('Restarting services: {}'.format(', '.join(services)))
        return bool(services)

    def cleanup(self, configs):
        present = set(glob.glob(p.join(self.prefix, 'conf.d/net.d/iface.*')))
        desired = set(c.path(self.prefix) for c in configs)
        remove = present - desired
        if not remove:
            return False
        if not self.do:
            self.echo('Would remove superfluous config files: {}'.
                      format(', '.join(remove)))
            return True
        self.echo('Removing superfluous config files: {}'.
                  format(', '.join(remove)))
        for f in remove:
            os.unlink(f)
        return True


def apply_configs(configs, prefix, do_edit, do_restart):
    desired = functools.reduce(set.union, (c.svc for c in configs))
    svcmgr = OpenRC(prefix=prefix, do=do_restart)
    enabled = svcmgr.enabled()
    running = svcmgr.running()
    svcmgr.disable(enabled - desired)
    svcmgr.stop(running - desired)
    need_restart = set()
    changed = False
    for config in configs:
        if config.apply(prefix, do_edit):
            need_restart.update(config.svc)
            changed = True
    svcmgr.cleanup(configs)
    svcmgr.enable(desired - enabled)
    svcmgr.restart(need_restart & running)
    svcmgr.start(desired - running)
    return changed | svcmgr.changed
