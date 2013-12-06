#!/usr/bin/env python
import sys

import pygtk
pygtk.require ('2.0')
import gtk

import lcm
from messages import *

class Msg_dialog (gtk.Dialog):
    def __init__ (self, module, msg):
        super (Msg_dialog, self).__init__ ('%s---%s' % (module, msg))

        modtype = getattr (lcmtypes, module)
        msgtype = getattr (modtype, msg)
        self.vals = getattr (msgtype, '__slots__')
        
        self.entries = {}
        table = gtk.Table (len (self.vals), 2)
        for ii,v in enumerate (self.vals):
            # should fill with default type, else bring up other dialog for
            # nested types
            self.entries[v] = gtk.Entry ()
            self.entries[v].set_editable (True)
            table.attach (gtk.Label (v), 0,1,ii,ii+1)
            table.attach (self.entries[v], 1,2,ii,ii+1)
        self.vbox.pack_start (table)

        self.vbox.pack_start (gtk.HSeparator ())
        self.add_button ('Broadcast', 1)
        self.add_button ('Cancel', 0)
        self.vbox.show_all ()

    def publish (self):
        print 'publish'

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
        while dlg.run ()!=0:
            dlg.publish ()
        dlg.destroy ()

    def on_main_window_destroy (self, widget):
        gtk.main_quit ()

    def run (self):
        gtk.main ()

if __name__ == '__main__':
    win = Command_window ()
    win.run ()

    sys.exit (0)
