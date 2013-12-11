##lcm-send
-----
lcm-spy equivalent for firing one-off lcm messages.

###Comments
-----
We can build a list of available lcm modules and types assuming a known
lcmtypes module structure. The user selects a type, which prompts a dialog box
for the user to fill the necessary message fields. Finally, the user submits
the message with a channel name to publish.

lcmtype attributes are specified by the `__slots__` member variable.
(see [Section 3.4.2.4
here](http://docs.python.org/2/reference/datamodel.html)). Unfortunately, we
cannot easily ascertain the type for both nested lcmtypes and lists.

* __lcmtypes:__ Nested lcmtypes are set to `NoneType` in the constructor, so
  we can assume that `NoneType` attributes are, in fact, nested lcmtypes. For
  now, we'll prompt the user to select the correct subtype. The `encode`
  function of the lcmtype verifies that the fingerprint of the subtype field
  matches the subtype fingerprint.
* __lists:__ Lists are tricky because Python lists can hold multiple types at
  once. For lack of any better ideas, we'll prompt the user to select the
  correct type for list members.
    * Fixed length arrays are lists initialized with the default length and
      values (again, `NoneType` for lists of nested lcmtypes). Because of the
      default value, we can determine the type of fixed length arrays.
    * Variable length arrays do not give any hint about their type, so we'll
      force the user to manually select this for now (even for primitive
      types, e.g., ints, floats, ...).
    * Variable length arrays must have length equal to that specified by
      another attribute (e.g., `nranges` specifies length of `ranges` array in
      `planar_lidar_t`). We'll rely on the user to fill in the length field.
    * Byte arrays... python lcm objects try to encode byte arrays as strings
      (or read-only char buffers), but a list is not read-only... so, really,
      we need to make sure lists that are intended to be byte arrays are set
      as strings.

A few ideas for moving forward:

* Cache attribute types for each lcmtype. The cache variables could consist of
  a dict from message name to attribute types. For example, a
  `senlcm.easydaq_t` contains a relay field that is a fixed length array of
  `relay_t`. We could write to cache a attributetypes dict such that
  `attributetypes['senlcm']['easydaq_t']['relay'] = list (relay_t)`. Or
  something to that effect. Could think about filling cache variables a few
  different ways:  
    * Parse the lcmdefs directory (one and done, could call from the UI).
    * Use manual completion method (as above).  
* Explore a Java implementation. Java allows introspection and is strongly
  typed.

Possible improvements for the Python implementation:

* Print enums/consts in dialog so that users can easily complete fields, or
  even better, somehow associate enums/consts with type and have drop-down
  menu.
* The UI is pretty clunky now. Essentially the user is asked to set messages
  (and recursively set messages for nested types and lists) through a series
  of pop-up dialogs. An lcm-spy style drop-down dialog recursion would
  probably be a little cleaner.

###Run
-----
`lcmtypes` are imported locally, but could be imported from an installed
module. To run from python dir:

$ ./lcm-send.py  

1. Select the module name, and message type.
2. Set message, and all other sets recursively (from lists and nested types).
   `set` stores the message object, `return` returns the object to the parent.
3. Write channel name.
4. Publish. Can publish the same object multiple times or set a new message.

###Authors -----
Perceptual robotics laboratory (PeRL) <jmwalls@umich.edu>
