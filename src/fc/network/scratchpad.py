# clean up old Puppet conffiles
for fn in glob.glob(p.join(rulesd, '70-persistent-net*')):
    os.unlink(fn)

