##lcmsend
-----
Lcm-spy equivalent for firing one-off lcm messages.

###Notes
-----
We can build a list of available lcm modules and types assuming a known
install structure. The user selects a type, which prompts a dialog box for the
user to fill the necessary message fields. Finally, the user submits the
message with a channel name to publish.

Message type fields are specified by the `__slots__` member variable.
Unfortunately, we cannot easily ascertain the type for both nested lcmtypes
and lists.

* __lcmtypes:__ Nested lcmtypes are set to `NoneType`, so we can assume that
  `NoneType` attributes are, in fact, nested lcmtypes. For now, we'll prompt
  the user to select the correct subtype. The `encode` function verifies that
  the fingerprint of the subtype field matches the subtype fingerprint.
* __lists:__ Lists are tricky because Python lists can hold multiple types at
  once. For lack of any better ideas, we'll prompt the user to select the
  correct type for list members.
    * Fixed length arrays are lists initialized with the default length.
    * Variable length arrays must have length equal to that specified by
      another attribute (e.g., `nranges` specifies length of `ranges` array in
      `planar_lidar_t`. We'll rely on the user to fill in the length field.
    * Byte arrays... LCM python types try to encode the byte array as strings
      (or read-only char buffers), but a list is not read-only... so, really,
      we need to make sure lists that are intended to be byte arrays are set
      as strings.

For more on Python class mechanics, including `__slots__`, see
[Section 3.4.2.4 here](http://docs.python.org/2/reference/datamodel.html).

A few ideas and extensions for moving forward:

* Use manual completion method (as above), but also cache user-specified
  values, e.g., nested lcmtype types.
* Parse the lcmdef directly (reluctant to do this---what if we only have the
  generated lcmtype).
* Leverage some other introspection tools...
* Play games with `encode` function; try to guess types until we don't raise
  an exception.
* Print enums/consts in dialog so that users can easily complete fields, or
  even better, somehow associate enums/consts with type and have drop-down
  menu.
* Explore a java implementation.

###Run
-----
`lcmtypes` are imported from the installed `perls` module. This path attribute
could be changed later or maybe allow manual specification. To run from python
dir:

$ ./lcmsend.py  


###Authors
-----
Perceptual robotics laboratory (PeRL) <jmwalls@umich.edu>
