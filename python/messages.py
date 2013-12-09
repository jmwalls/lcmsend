import types
from perls import lcmtypes

modules = [m for m in dir (lcmtypes) if not '__' in m]
messages = {m:[t for t in dir (getattr (lcmtypes,m)) if not '__' in t] 
        for m in modules}

defaults = {types.IntType : '0',
            types.FloatType : '0.0',
            types.BooleanType : 'False',
            types.StringType : ''}

def str_to_type (t, val):
    """
    convert string argument to specified type

    Parameters
    -----------
    t : type objec
    val : string value

    Raises
    -------
    ValueError if the type cannot be converted properly

    Notes
    ------
    Booleans are a little weird, as long as the string containts a 't', we
    return true, else return false.
    """
    if t==types.IntType:
        return int (val)
    elif t==types.FloatType:
        return float (val)
    elif t==types.BooleanType:
        if 't' in val.lower (): return True
        else: return False
    elif t==types.StringType:
        return val
    else:
        raise ValueError ('Unsupported type %s' % t.__name__)


class Message (object):
    """
    Lcm Message object---decomposes lcm messages into blanks (primitive
    fields), lists (of type primitive or Lcm message), and nested Lcm
    Messages.

    Parameters
    -----------
    lcmobj : instance of lcmtype

    vals : message attributes
    types : type of each val

    blanks : list of primitive attributes
    lists : list of list attributes
    nests : list of nested attributes
    """
    def __init__ (self, mod, msg):
        modtype = getattr (lcmtypes, mod)
        msgtype = getattr (modtype, msg)

        self.vals = getattr (msgtype, '__slots__')
        self.lcmobj = msgtype ()

        self.types, self.blanks, self.lists, self.nests = {},[],[],[]
        for v in self.vals:
            t = type (getattr (self.lcmobj, v))
            self.types[v] = t

            if t==types.NoneType: self.nests.append (v)
            elif t==types.ListType: self.lists.append (v)
            else: self.blanks.append (v)

    def set_value (self, attr, val):
        pass



if __name__ == '__main__':
    print 'messages module test---listing available lcm modules and messages'

    for m,vals in types.iteritems ():
        print m
        for v in vals: print '\t', v
