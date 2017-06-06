README
======

Terminology
-----------

We model a bunch of concepts which are quite similar to each other. To keep a
sane mind, specific terminology for various kinds of network entities will be
used throughout the code.

Virtualized networking is set up in a stacked way: what is an inner interface to
a host is an outer interface to a VM. The following terminology applies both to
physical and virtual machines according to their respective point of view.

- Port: outwards directed thing. Has a MAC address and is attached to some
  piece of network gear like a physical switch or a host bridge.

- Interface: inwards directed thing. Has IP addresses and is accessed by network
  applications.

- Tag interface: Interface which received traffic for only one VLAN ID on tagged
  ports.

In the case of an unbridged interface on an untagged port, all 3 entities are
named the same.
