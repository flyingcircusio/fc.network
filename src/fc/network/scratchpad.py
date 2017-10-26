"""Random stuff to incorporate into the right place later on."""

import glob
import os


# clean up old Puppet conffiles
for fn in glob.glob('70-persistent-net*'):
    os.unlink(fn)
