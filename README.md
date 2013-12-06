##lcmsend
-----
Lcm-spy equivalent for firing one-off lcm messages.

###Notes
-----
We can build a list of available lcm modules and types. The user selects a
type, which prompts a dialog box for the user to fill the necessary message
fields. Finally, the user submits the message with a channel name to publish.

Message type fields are specified by the `__slots__` attribute. Unfortunately,
we cannot easily ascertain the type for both nested lcmtypes and lists.

* __lcmtypes:__ Nested lcmtypes are set to `NoneType`, so we can assume that
  `NoneType` attributes are, in fact, nested lcmtypes. For now, we'll prompt
  the user to select the correct subtype.
* __lists:__ Lists are tricky because Python lists can hold mutliple types.
  For lack of any better ideas, we'll prompt the user to select the correct
  type for list members, and manually complete the length field.
    * Fixed length arrays are lists initialized with the default length.
    * Variable length arrays must have length equal to that specified by
      another attribute (e.g., `nranges` specifies length of `ranges` array in
      `planar_lidar_t`.

A few options for moving forward:

* Use manual completion method (as above), but cache user specified values.
* Parse the lcmdef.
* Leverage some other introspection tools...
* Print enums in dialog

###Run
-----
`lcmtypes` are imported from the installed `perls` module. This path attribute
could be changed later or maybe allow manual specification. To run:

$ ./lcmsend.py  


###Authors
-----
Perceptual robotics laboratory (PeRL) <jmwalls@umich.edu>
