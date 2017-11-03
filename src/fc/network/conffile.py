"""Configuration file + related openrc services."""

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

    def diff(self, other, prefix=''):
        diff = list(difflib.unified_diff(
            other.content.splitlines(), self.content.splitlines(),
            p.join(prefix, other.relpath), p.join(prefix, self.relpath)))
        if self.svc != other.svc:
            diff += ["\nServices: {} != {}".format(other.svc, self.svc)]
        return '\n'.join(diff)
