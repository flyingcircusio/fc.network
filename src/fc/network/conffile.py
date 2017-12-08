"""Configuration file + related openrc services."""

import click
import difflib
import glob
import orderedset
import os
import os.path as p

set = orderedset.OrderedSet


class Conffile():

    def __init__(self, relpath, content, svc=set()):
        """Describes a configuration file with associated services.

        relpath: file path relative to the conf root (e.g., /etc)
        content: text
        svc: set of services that must be restarted if file contents
            have changed.
        """
        self.relpath = relpath
        self.content = content
        self.svc = svc

    def __eq__(self, other):
        return (self.relpath == other.relpath and
                self.content == other.content and
                self.svc == other.svc)

    def diff(self, other=None, prefix=''):
        diff = list(difflib.unified_diff(
            other.content.splitlines(True), self.content.splitlines(True),
            p.join(prefix, other.relpath), p.join(prefix, self.relpath)))
        return ''.join(diff)

    def path(self, prefix):
        return p.join(prefix, self.relpath)

    def write(self, prefix, do=True):
        """Edits file on disk or pretends to do so.

        Returns True is anything (has been|should be) changed.
        """
        path = self.path(prefix)
        try:
            with open(path) as f:
                old = f.read()
            if old == self.content:
                return False
        except IOError:
            old = ''
        if not do:
            click.secho('NO-DO: ', nl=False, fg='yellow')
        click.echo('Editing configuration file {}:\n{}'.format(
            path,
            ''.join(difflib.unified_diff(
                old.splitlines(True), self.content.splitlines(True),
                path, path))))
        if do:
            os.makedirs(p.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(self.content)
        return True


def writeall(configs, prefix, do=True):
    restart_svc = set()
    for config in configs:
        if config.write(prefix, do):
            restart_svc.update(config.svc)
    return restart_svc


def cleanup(present, desired, do=True):
    """Unmanage stale files.

    `present` is a glob expression which defines the cleanup scope
    (e.g., /path/to/iface.*).
    `desired` is a set or generator of config files to keep.
    Note that it is best to specify absolute paths for both parameters.
    Returns True if anything (has been|would have been) deleted.
    """
    present = set(glob.glob(present))
    desired = set(desired)
    remove = present - desired
    if not remove:
        return False
    if not do:
        click.secho('NO-DO: ', nl=False, fg='yellow')
    click.echo('Removing superfluous config files: {}'.
               format(', '.join(remove)))
    if do:
        for f in remove:
            os.unlink(f)
    return True
