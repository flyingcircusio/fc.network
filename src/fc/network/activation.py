from .conffile import cleanup
import click
import functools
import glob
import os
import os.path as p
import re
import subprocess


class OpenRC:

    _rl = None
    _initd = None

    def __init__(self, runlevel='default', prefix='/etc', do=True):
        self.runlevel = runlevel
        self.prefix = prefix
        self.do = do
        self.changed = False

    @property
    def rl(self):
        """Runlevel registration dir. Created if nonexistent."""
        if not self._rl:
            self._rl = p.join(self.prefix, 'runlevels', self.runlevel)
            os.makedirs(self._rl, exist_ok=True)
        return self._rl

    @property
    def initd(self):
        """Init script dir. Created if nonexistent."""
        if not self._initd:
            self._initd = p.join(self.prefix, 'init.d')
            os.makedirs(self._initd, exist_ok=True)
        return self._initd

    def echo(self, *args, **kw):
        if not self.do:
            click.secho("NO-DO: ", nl=False, fg='yellow')
        click.secho(*args, **kw)

    R_STARTED = re.compile(r'^\s*(\S+)\s+\[\s+started\s+\]$')

    def running(self, filter='net.'):
        res = set()
        for line in subprocess.check_output(
                ['rc-status', '-a', '-C']).decode('ascii').splitlines():
            m = self.R_STARTED.match(line)
            if m:
                svc = m.group(1)
                if svc.startswith(filter) and svc != 'net.lo':
                    res.add(svc)
        return res

    def enabled(self, filter='net.'):
        res = set()
        for f in glob.glob(p.join(self.rl, '*')):
            svc = p.basename(f)
            if svc.startswith(filter) and svc != 'net.lo':
                if p.islink(f) and p.exists(f):
                    res.add(svc)
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
            if svc.startswith('net.'):
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
            if svc.startswith('net.'):
                changed |= self._symlink('net.lo', init)
            changed |= self._symlink(init, p.join(self.rl, svc))
        return changed

    def stop(self, services):
        for svc in services:
            self.echo('Stopping service: {}'.format(svc))
            initd = p.join(self.initd, svc)
            if self.do:
                subprocess.check_call([initd, 'stop'])
        return bool(services)

    def start(self, services):
        for svc in services:
            self.echo('Starting service: {}'.format(svc))
            initd = p.join(self.initd, svc)
            if self.do:
                subprocess.check_call([initd, 'start'])
        return bool(services)

    def restart(self, services):
        for svc in services:
            self.echo('Restarting service: {}'.format(svc))
            initd = p.join(self.initd, svc)
            if self.do:
                subprocess.check_call([initd, 'restart'])
        return bool(services)


def apply_configs(configs, prefix, do_edit, do_restart):
    desired = functools.reduce(set.union, (c.svc for c in configs))
    svcmgr = OpenRC(prefix=prefix, do=do_restart)
    enabled = svcmgr.enabled()
    click.secho('Enabled services: {}'.format(', '.join(enabled)), fg='green')
    running = svcmgr.running()
    click.secho('Running services: {}'.format(', '.join(running)), fg='green')
    svcmgr.disable(enabled - desired)
    svcmgr.stop(running - desired)
    need_restart = set()
    changed = False
    for config in configs:
        if config.apply(prefix, do_edit):
            need_restart.update(config.svc)
            changed = True
    cleanup(p.join(prefix, 'conf.d/net.d/iface.*'),
            (p.join(prefix, c.relpath) for c in configs),
            do_edit)
    svcmgr.enable(desired - enabled)
    svcmgr.restart(need_restart & running)
    svcmgr.start(desired - running)
    return changed | svcmgr.changed
