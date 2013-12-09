#!/usr/bin/env python
import sys
import time
import types

import pygtk
pygtk.require ('2.0')
import gtk

import lcm
from perls import lcmtypes

modules = [m for m in dir (lcmtypes) if not '__' in m]
messages = {m:[t for t in dir (getattr (lcmtypes,m)) if not '__' in t] 
        for m in modules}
primitives = [types.IntType,
              types.FloatType,
              types.BooleanType,
              types.StringType]
defaults = {types.IntType : '0',
            types.FloatType : '0.0',
            types.BooleanType : 'False',
            types.StringType : '',
            types.NoneType : None}

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
    elif t==types.NoneType:
        return None
    else:
        raise ValueError ('Unsupported type %s' % t.__name__)


class Message (object):
    """
    Lcm Message object---decomposes lcm messages into blanks (primitive
    fields), lists (of type primitive or Lcm message), and nested Lcm
    Messages.

    Parameters
    -----------
    modtype : list of lcmtypes in module
    msgtype : requested lcmtype

    lcmobj : instance of lcmtype

    vals : message attributes (defined by __slots__)
    nvals : number of vals
    types : type of each val

    blanks : list of primitive attributes
    lists : list of list attributes
    nests : list of nested attributes
    """
    def __init__ (self, mod, msg):
        self.modtype = getattr (lcmtypes, mod)
        self.msgtype = getattr (self.modtype, msg)

        self.vals = getattr (self.msgtype, '__slots__')
        self.nvals = len (self.vals)
        self.lcmobj = self.msgtype ()

        self.types, self.blanks, self.lists, self.nests = {},[],[],[]
        for v in self.vals:
            t = type (getattr (self.lcmobj, v))
            self.types[v] = t

            if t==types.NoneType: self.nests.append (v)
            elif t==types.ListType: self.lists.append (v)
            else: self.blanks.append (v)

    def set_value (self, attr, val):
        setattr (self.lcmobj, attr, val)

    def value (self, attr):
        return getattr (self.lcmobj, attr)

def timestamp ():
    return int (time.time ()*1e6)


class Entry_box (gtk.HBox):
    """
    entry base class---each entry is a user field for inputing a message
    attribute

    Parameters
    -----------
    val : value name
    """
    def __init__ (self, val):
        super (Entry_box, self).__init__ ()
        self.val = val

    def get_value (self):
        raise NotImplementedError


class Text_box (Entry_box):
    """
    entry box for all primitive fields (int,float,bool,str)

    Parameters
    -----------
    t : entry type
    """
    def __init__ (self, val, t):
        super (Text_box, self).__init__ (val)
        self.type = t

        self.entry = gtk.Entry ()
        self.entry.set_editable (True)
        if (val=='utime'): self.entry.set_text (str (timestamp ()))
        else: self.entry.set_text (defaults[t])

        self.pack_start (self.entry, expand=True, fill=True)
        self.show ()

    def get_value (self):
        strval = self.entry.get_text ()
        val = str_to_type (self.type, strval)
        print self.val, val
        return val


class List_dialog (gtk.Dialog):
    """
    list dialog object handles specifying a list attribute

    Parameters
    -----------
    val : value name
    t : list value type
    length : fixed length, or None for variable length
    """
    def __init__ (self, module, val, t, length=None):
        super (List_dialog, self).__init__ ('List')
        self.length, self.t = length, t
        self.l = []
        if t==types.NoneType: self.entry = Nest_box (module, val)
        else: self.entry = Text_box (val,t)
        self.vbox.pack_start (self.entry, expand=True, fill=True)

        add = gtk.Button ('Add')
        add.connect ('clicked', self._on_add)
        self.vbox.pack_start (add, expand=True, fill=True)

        clear = gtk.Button ('Clear')
        clear.connect ('clicked', self._on_clear)
        self.vbox.pack_start (clear, expand=True, fill=True)

        self.vbox.pack_start (gtk.HSeparator (), expand=True, fill=True)
        self.add_button ('Return', 1)
        self.add_button ('Cancel', 0)
        self.vbox.show_all ()

    def _on_add (self, widget):
        if not self.length is None and len (self.l) >= self.length:
            print 'already added specified length'
            return
        self.l.append (self.entry.get_value ())

    def _on_clear (self, widget):
        self.l = []

    def list (self):
        if not self.length is None:
            l = [str_to_type (self.t, defaults[self.t]) for _ in range (self.length)]
            l[:len (self.l)] = self.l
            return l
        return self.l


class List_box (Entry_box):
    """
    entry box for list types

    Parameters
    -----------
    setval : value that lcmobj is currently set to, if list already has a
        length, then we assume that the type has a fixed length array. 
    """
    def __init__ (self, module, val, setval):
        super (List_box, self).__init__ (val)
        self.module = module
        self.type = types.NoneType
        self.lvals, self.length = None, None

        lsv = len (setval)
        if lsv>0:
            self.length = lsv
            self.type = type (setval[0])
            self.lvals = setval
            if self.type != types.NoneType:
                label = gtk.Label ('%s[%d]'%(self.type.__name__,lsv))
                self.pack_start (label, expand=True, fill=True)
            else: 
                label = gtk.Label ('Lcmtype[%d]'%lsv)
            self.pack_start (label, expand=True, fill=True)
        else:
            self.length = None
            self._init_type (module)

        button = gtk.Button ('Set')
        button.connect ('clicked', self._on_set)
        self.pack_start (button, expand=True, fill=True)

        self.show ()

    def _init_type (self, module):
        if self.type != types.NoneType: return
        self.cbmsg = gtk.combo_box_new_text ()
        self.ptypes = primitives[:]
        self.ptypes.append (types.NoneType)
        for m in self.ptypes:
            self.cbmsg.append_text (m.__name__)
        self.cbmsg.set_active (0)
        self.pack_start (self.cbmsg, expand=True, fill=True)

    def _on_set (self, widget):
        if self.length is None and self.type==types.NoneType:
            self.type = self.ptypes[self.cbmsg.get_active ()]
        dlg = List_dialog (self.module, self.val, self.type, self.length)
        if dlg.run ()==1:
            self.lvals = dlg.list ()
            print self.lvals
        dlg.destroy ()

    def get_value (self):
        if not self.lvals: return []
        return self.lvals


class Nest_box (Entry_box):
    """
    entry box for nested type
    """
    def __init__ (self, module, val):
        super (Nest_box, self).__init__ (val)
        self.module = module

        self.cbmsg = gtk.combo_box_new_text ()
        msgs = messages[module]
        for m in msgs:
            self.cbmsg.append_text (m)
        self.cbmsg.set_active (0)
        self.pack_start (self.cbmsg, expand=True, fill=True)

        button = gtk.Button ('Set')
        button.connect ('clicked', self._on_set)
        self.set = False

        self.pack_start (button, expand=True, fill=True)
        self.show ()

    def _on_set (self, widget):
        msg = messages[self.module][self.cbmsg.get_active ()]
        dlg = Msg_dialog (self.module, msg)
        if dlg.run ()==1:
            self.msg = dlg.message ()
        dlg.destroy ()
        self.set = True

    def get_value (self):
        if not self.set: return
        return self.msg


class Msg_dialog (gtk.Dialog):
    """
    message dialog object handles specifying an lcm message

    Parameters
    -----------
    msg : message instance
    channel : channel to publish over (only if base message)

    Notes
    ------
    Want object to recursively return an lcm message object, so that we can
    handle nested types and lists with the same framework.
    """
    def __init__ (self, module, msgname):
        super (Msg_dialog, self).__init__ (msgname)
        self.module = module

        self.table = self._init_table (msgname)
        self.vbox.pack_start (self.table, expand=True, fill=True)

        self.vbox.pack_start (gtk.HSeparator (), expand=True, fill=True)
        self.add_button ('Return', 1)
        self.add_button ('Cancel', 0)
        self.vbox.show_all ()

    def _init_table (self, mname):
        self.msg = Message (self.module, mname)

        self.entries, nentries = {}, self.msg.nvals
        table = gtk.Table (nentries, 3)
        for ii,v in enumerate (self.msg.vals):
            t = self.msg.types[v]
            table.attach (gtk.Label (v), 0,1,ii,ii+1)
            table.attach (gtk.Label (t.__name__), 2,3,ii,ii+1)

            if t==types.NoneType: 
                e = Nest_box (self.module, v)
            elif t==types.ListType: 
                e = List_box (self.module, v, self.msg.value (v))
            else: 
                e = Text_box (v, t)
            self.entries[v] = e
            table.attach (e, 1, 2, ii, ii+1)
        return table

    def message (self):
        """
        return message instance
        """
        for v in self.msg.vals:
            val = self.entries[v].get_value ()
            self.msg.set_value (v, val)

        return self.msg.lcmobj


class Command_window (object):
    """
    Command_window---main lcmsend GUI object

    specifies lcm module, channel, and prompts user with message dialog

    Parameters
    -----------
    window : underlying gtk window
    lcm : lcm object
    """
    def __init__ (self):
        self.window = gtk.Window ()
        self.window.set_title ('Lcmsend')
        self.window.set_default_size (400,200)
        self.window.set_position (gtk.WIN_POS_CENTER)
        self.window.connect ('destroy', self.on_main_window_destroy)

        self.vbox = gtk.VBox ()
        self.window.add (self.vbox)

        self.cbox = gtk.VBox ()
        self.cbmodule = gtk.combo_box_new_text ()
        for m in modules:
            self.cbmodule.append_text (m)
        self.cbmodule.set_active (0)
        self.cbox.pack_start (self.cbmodule, fill=False, expand=False)
        self._update_msgs ()
        self.cbmodule.connect ('changed', self._on_module)

        self.vbox.pack_start (self.cbox, fill=True, expand=True)

        self.channel = gtk.Entry ()
        self.channel.set_editable (True)
        self.channel.set_text ('CHANNEL')
        self.vbox.pack_start (self.channel, fill=True, expand=True )

        setbutton = gtk.Button ('Set message')
        setbutton.connect ('clicked', self._on_set)
        self.vbox.pack_start (setbutton, fill=True, expand=True)

        pubbutton = gtk.Button ('Publish')
        pubbutton.connect ('clicked', self._on_publish)
        self.vbox.pack_start (pubbutton, fill=True, expand=True)

        self.window.show_all ()

        self.msg = None
        self.lcm = lcm.LCM ()

    def _update_window (self):
        while gtk.events_pending ():
            gtk.main_iteration_do (True)

    def _update_msgs (self):
        self.cbmsg = gtk.combo_box_new_text ()
        msgs = messages[modules[self.cbmodule.get_active ()]]
        for m in msgs:
            self.cbmsg.append_text (m)
        self.cbmsg.set_active (0)
        self.cbmsg.show ()
        self.cbox.pack_start (self.cbmsg, fill=False, expand=False)

    def _on_module (self, combo):
        self.cbox.remove (self.cbmsg)
        self._update_msgs ()
        self.cbox.queue_draw ()
        self._update_window ()

    def _on_set (self, widget):
        mod = modules[self.cbmodule.get_active ()]
        msg = messages[mod][self.cbmsg.get_active ()]
        dlg = Msg_dialog (mod,msg)
        if dlg.run ()==1: 
            self.msg = dlg.message ()
        dlg.destroy ()

    def _on_publish (self, widget):
        if not self.msg: 
            print 'no message specified, set message first'
            return
        channel = self.channel.get_text ()
        try:
            self.lcm.publish (channel, self.msg.encode ())
            print '%d published' % (timestamp ())
        except Exception as e:
            print '%d error publishing message: %s' % (timestamp (), e)
            raise

    def on_main_window_destroy (self, widget):
        gtk.main_quit ()

    def run (self):
        gtk.main ()


if __name__ == '__main__':
    win = Command_window ()
    win.run ()

    sys.exit (0)
