import types
from perls import lcmtypes

modules = [m for m in dir (lcmtypes) if not '__' in m]
messages = {m:[t for t in dir (getattr (lcmtypes,m)) if not '__' in t] 
        for m in modules}

defaults = {'int' : '0',
            'float' : '0.0',
            'boolean' : 'False',
            'str' : ''}

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
        if 't' in val.lower: return True
        else: return False
    elif t==types.StringType:
        return val
    else:
        raise ValueError ('Unsupported type %s' % t.__name__)


if __name__ == '__main__':
    print 'messages module test---listing available lcm modules and messages'

    for m,vals in types.iteritems ():
        print m
        for v in vals: print '\t', v
