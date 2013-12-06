from perls import lcmtypes

modules = [m for m in dir (lcmtypes) if not '__' in m]
messages = {m:[t for t in dir (getattr (lcmtypes,m)) if not '__' in t] 
        for m in modules}


if __name__ == '__main__':
    print 'messages module test---listing available lcm modules and messages'

    for m,vals in types.iteritems ():
        print m
        for v in vals: print '\t', v
