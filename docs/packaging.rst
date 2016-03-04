Packaging
=========

For those interested in packaging RIPE Atlas Tools for their favourite distro,
this section is for you.

Currently Supported
-------------------

* OpenBSD
* FreeBSD
* Gentoo
* Debian
* Ubuntu

In Progress
-----------

* Fedora: Jan Včelák is currently building the binary packages in `COPR`_ (which will take some time as there is a lot of other packages in the queue)

.. _`COPR`: https://copr.fedoraproject.org/coprs/jvcelak/ripe-atlas-tools/

Additional Distributions
------------------------

Is your distribution not listed?  If you'd like to build a package for another
distro or even if you're just someone who knows someone who can help us package
and distribute this, please get in touch.

Further Information
-------------------

User Agent
~~~~~~~~~~

When packaging, it's good practise to manually set the user agent used within
the toolkit so that we can get a rough idea of which distros are using this
software.  This is easily done by writing an arbitrary string to
``<root>/ripe/atlas/tools/user-agent``.  Something like this is recommended:::

    RIPE Atlas Tools (Magellan) [FreeBSD 10.2] 1.2

The only limitations to this file are that it should:

* Only have one line in it (all other will be ignored)
* That line should have a maximum of 128 characters in it
