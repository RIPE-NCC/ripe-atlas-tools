.. image:: https://readthedocs.org/projects/ripe-atlas-tools/badge/?version=latest
  :target: http://ripe-atlas-tools.readthedocs.org/en/latest/?badge=latest
  :alt: Documentation Status

RIPE Atlas Tools (Magellan)
===========================

The official command-line client for RIPE Atlas.


Disclaimer
----------

All of this is super-beta.  If it breaks, you get to keep all the shiny pieces.


Full Documentation
------------------

Everything is up on `ReadTheDocs`_

.. _ReadTheDocs: https://ripe-atlas-tools.readthedocs.org/


How Does it Work?
-----------------

Presently, the setup is pretty crude.  You can create a ping or traceroute
measurement with limited options from the command line:

.. code:: bash

    $ ripe-atlas measure ping --target example.com
    $ ripe-atlas measure ping --packets 7 --size 42 --target example.com
    $ ripe-atlas measure traceroute --target example.com
    $ ripe-atlas measure traceroute --packets 2 --target example.com
    $ ripe-atlas measure dns --query-argument example.com
    $ ripe-atlas measure dns --use-probe-resolver --query-type AAAA --query-argument example.com

This will create a one-off measurement and then wait for the results to roll in,
formatting them as they do.

You can also use it to connect to a stream of formatted data.  This command will
start streaming out all of the results from one of our oldest measurements:

.. code:: bash

    $ ripe-atlas stream 1001

Or you can generate a simple report:

.. code:: bash

    $ ripe-atlas report 1001

Configuration is done by way of a config file, and modifying it can be done from
the command line:

.. code:: bash

    $ ripe-atlas configure --set authorisation.create=MY_API_KEY


Can I Contribute?
-----------------

Absolutely.  Please read our `guide`_ on how to contribute.

.. _guide: https://github.com/RIPE-NCC/ripe-atlas-tools/blob/master/CONTRIBUTING.rst


Colophon
--------

This project was code-named by means of a `poll`_.  In order to conform to the
RIPE Atlas theme, it had to be named for an explorer, and so the winning
suggestion was for Magellan, *"in memory of those times when RTT was ~3 years"*.

.. _poll: https://github.com/RIPE-NCC/ripe-atlas-tools/issues/13
