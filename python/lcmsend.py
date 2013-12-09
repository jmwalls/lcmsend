#!/usr/bin/env python
import sys
import time

import pygtk
pygtk.require ('2.0')
import gtk

import lcm
from messages import *

def timestamp ():
    return int (time.time ()*1e6)


class Msg_dialog (gtk.Dialog):
    """
    dialog object handles specifying and publishing the message

    Parameters
    -----------
    msg : message instance
    vals : user configurable message attributes (defined by __slots__)
    entries : user specified vals
    channel : channel to publish over

    Notes
    ------
    Want object to recursively return an lcm message object, so that we can
    handle nested types and lists with the same framework.
    """
    def __init__ (self, module, msg):
        super (Msg_dialog, self).__init__ (msg)
        self.label = msg
        self.mval = Msg_values (module,msg)

        self.entries, nentries = {}, len (mval.vals)
        table = gtk.Table (nentries, 3)
        for ii,v in enumerate (mval.vals):
            t = mval.types[v]
            table.attach (gtk.Label (v), 0,1,ii,ii+1)
            table.attach (gtk.Label (t.__name__), 2,3,ii,ii+1)

            if t==types.NoneType: 
                continue # should prompt user
            elif t==types.ListType: 
                continue # should prompt user

            e = gtk.Entry ()
            e.set_editable (True)
            if (v=='utime'): e.set_text (str (timestamp ()))
            else: e.set_text (defaults[t])
            table.attach (e, 1, 2, ii, ii+1)
            self.entries[v] = e
        self.vbox.pack_start (table, expand=True, fill=True)

        self.channel = gtk.Entry ()
        self.channel.set_editable (True)
        self.channel.set_text ('_'.join ([self.label.upper (),'CHANNEL']))
        self.vbox.pack_start (self.channel, expand=True, fill=True)

        self.vbox.pack_start (gtk.HSeparator (), expand=True, fill=True)
        self.add_button ('Broadcast', 1)
        self.add_button ('Cancel', 0)
        self.vbox.show_all ()

    def message (self):
        for v in self.vals:
            t = type (getattr (self.msg, v))

            if t==types.NoneType: 
                continue # do something
            elif t==types.ListType:
                setattr (self.msg, v, []) # set empty for now
            else:
                try:
                    val = str_to_type (t, self.entries[v].get_text ())
                    setattr (self.msg, v, val)
                except Exception as e:
                    print 'uh oh: %s' % e
                    return
        return self.msg

    def channel (self):
        channel = self.channel.get_text ()
        return channel


class Command_window (object):
    """
    Command_window---main lcmsend GUI object

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

        cbframe = gtk.Frame ('LCM Messages')
        self.cbbox = gtk.VBox ()
        cbframe.add (self.cbbox)
        self.vbox.pack_start (cbframe, fill=False, expand=False)

        self.cbmodule = gtk.combo_box_new_text ()
        for m in modules:
            self.cbmodule.append_text (m)
        self.cbmodule.set_active (0)
        self.cbmodule.connect ('changed', self.on_combo_changed)
        self.cbbox.pack_start (self.cbmodule, fill=False, expand=False)

        self.update_messages ()

        button = gtk.Button ('Publish')
        button.connect ('clicked', self.on_publish)
        self.vbox.pack_start (button, fill=True, expand=True)

        self.window.show_all ()

        self.lcm = lcm.LCM ()

    def update_window (self):
        while gtk.events_pending ():
            gtk.main_iteration_do (True)

    def update_messages (self):
        self.cbmsg = gtk.combo_box_new_text ()
        msgs = messages[modules[self.cbmodule.get_active ()]]
        for m in msgs:
            self.cbmsg.append_text (m)
        self.cbmsg.set_active (0)
        self.cbmsg.show ()
        self.cbbox.pack_start (self.cbmsg, fill=False, expand=False)

    def on_combo_changed (self, combo):
        self.cbbox.remove (self.cbmsg)
        self.update_messages ()
        self.cbbox.queue_draw ()
        self.update_window ()

    def on_publish (self, widget):
        mod = modules[self.cbmodule.get_active ()]
        msg = messages[mod][self.cbmsg.get_active ()]
        dlg = Msg_dialog (mod, msg)
        if dlg.run ()==1: 
            try:
                self.lcm.publish (dlg.channel (), dlg.message ())
                print '%d published %s' % (timestamp (), self.label)
            except Exception as e:
                print '%d error publishing %s: %s' % (timestamp (), self.label, e)
        #self.msg = dlg.message () # cache
        dlg.destroy ()

    def on_main_window_destroy (self, widget):
        gtk.main_quit ()

    def run (self):
        gtk.main ()


if __name__ == '__main__':
    win = Command_window ()
    win.run ()

    sys.exit (0)
