import os
import os.path as p


class PersistentItem:

    def __init__(self, path, content):
        self.path = path
        self.content = content

    def missing(self):
        return not p.exists(self.path)

    def update(self):
        raise NotImplementedError()

    @property
    def needs_update(self):
        return False


class Conffile(PersistentItem):

    def update(self):
        if not self.needs_update:
            return False
        os.makedirs(p.dirname(self.path), exist_ok=True)
        with open(self.path, 'w') as f:
            f.write(self.content)
            f.flush()
            os.fsync(f)
        return True

    @property
    def needs_update(self):
        try:
            with open(self.path) as f:
                return f.read() != self.content
        except EnvironmentError:
            return True


class Symlink(PersistentItem):

    def update(self):
        if not self.needs_update:
            return False
        os.makedirs(p.dirname(self.path), exist_ok=True)
        os.symlink(self.content, self.path)

    @property
    def needs_update(self):
        try:
            return os.readlink(self.path) != self.content
        except EnvironmentError:
            return True
