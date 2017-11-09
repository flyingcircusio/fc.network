"""Configuration file + related openrc services."""

import click
import difflib
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

    def apply(self, prefix='', do=True):
        path = p.join(prefix, self.relpath)
        try:
            with open(path) as f:
                old = f.read()
            if old == self.content:
                return False
        except IOError:
            old = ''
        click.echo('{} configuration file:\n{}'.format(
            'Editing' if do else 'Would edit',
            ''.join(difflib.unified_diff(
                old.splitlines(True), self.content.splitlines(True),
                path, path))))
        if do:
            with open(path, 'w') as f:
                f.write(self.content)
        return True
