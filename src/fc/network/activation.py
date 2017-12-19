from .conffile import writeall, cleanup
from .openrc import OpenRC
import click
import functools
import orderedset
import os.path as p
import subprocess

set = orderedset.OrderedSet


def matryoshka(activationsets):
    """Nest a stack of ActivationSets.

    The passed list must have the innermost ActivationSet first.
    Returns the outermost ActivationSet.
    """
    for i, actset in enumerate(activationsets):
        if i == 0:
            actset.inner = ActivationSet()
        if i > 0:
            actset.inner = activationsets[i - 1]
    return activationsets[-1]


class ActivationSet():

    inner = None  # to be set in matryoshka()

    def __init__(self, configs=None):
        self.configs = list(configs or [])

    def activate(self, prefix, do_edit, do_restart):
        """Activates all local configs.

        Calls out to the inner set's activate() method at an appropriate
        place.
        Returns True if anything (has been|should have been) changed.
        """
        if self.inner:
            return self.inner.activate(prefix, do_edit, do_restart)
        return False  # null implementation


class IfacesActivation(ActivationSet):

    def activate(self, prefix, do_edit, do_restart):
        svcmgr = OpenRC(prefix=prefix, do=do_restart)
        changed = False
        desired = functools.reduce(
            set.union, (c.svc for c in self.configs), set())
        enabled = svcmgr.enabled()
        click.secho('Enabled services: {}'.format(', '.join(enabled)),
                    fg='green')
        running = svcmgr.running()
        click.secho('Running services: {}'.format(', '.join(running)),
                    fg='green')
        svcmgr.disable(enabled - desired)
        svcmgr.stop(running - desired)
        need_restart = writeall(self.configs, prefix, do_edit)
        changed = super().activate(prefix, do_edit, do_restart)
        svcmgr.enable(desired - enabled)
        svcmgr.restart(need_restart & running)
        svcmgr.start(desired - running)
        changed |= cleanup(p.join(prefix, 'conf.d/net.d/iface.*'),
                           (p.join(prefix, c.relpath) for c in self.configs),
                           do_edit)
        return changed | bool(need_restart) | svcmgr.changed


class SingleConfigActivation(ActivationSet):

    def activate(self, prefix, do_edit, do_restart):
        assert len(self.configs) == 1, "There should be exactly one mactab"
        c = self.configs[0]
        changed_me = c.write(prefix, do_edit)
        changed_inner = super().activate(prefix, do_edit, do_restart)
        if changed_me:
            self.restart(prefix, do_restart)
        return changed_me | changed_inner

    def restart(self, prefix, do):
        raise NotImplementedError()


class MactabActivation(SingleConfigActivation):

    def restart(self, prefix, do):
        if do:
            c = self.configs[0]
            subprocess.check_call(['nameif', '-c', p.join(prefix, c.relpath)])


class UdevActivation(SingleConfigActivation):

    def restart(self, prefix, do):
        OpenRC(prefix=prefix, do=do).restart(['udev-trigger'])
