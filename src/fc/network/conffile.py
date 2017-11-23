"""Configuration file + related openrc services."""

import click
import difflib
import os
import os.path as p


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
        assert isinstance(svc, set)
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

    def apply(self, prefix, do=True):
        path = self.path(prefix)
        try:
            with open(path) as f:
                old = f.read()
            if old == self.content:
                return False
        except IOError:
            old = ''
        click.echo('{} configuration file {}:\n{}'.format(
            'Editing' if do else 'Would edit', path,
            ''.join(difflib.unified_diff(
                old.splitlines(True), self.content.splitlines(True),
                path, path))))
        if do:
            os.makedirs(p.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(self.content)
        return True
