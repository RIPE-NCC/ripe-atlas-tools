RIPE Atlas Tools (Magellan)
===========================
|Documentation| |Build Status| |PYPI Version| |Python Versions| |Python Implementations| |Python Format| |Requirements|

The official command-line client for RIPE Atlas.


Full Documentation
------------------

Everything is up on `ReadTheDocs`_


How Does it Work?
-----------------

Presently, the setup is pretty crude.  You can create a ping or traceroute
measurement with limited options from the command line:

.. code:: bash

    $ ripe-atlas measure ping --target example.com

    # or you can omit --target for most measurement types
    $ ripe-atlas measure ping example.com

    $ ripe-atlas measure ping --packets 7 --size 42 --target example.com

    $ ripe-atlas measure traceroute --target example.com

    $ ripe-atlas measure traceroute --packets 2 --target example.com

    $ ripe-atlas measure dns --query-argument example.com

    # or you can omit --query-argument for DNS measuremetns
    $ ripe-atlas measure dns example.com

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


Colophon
--------

This project was code-named by means of a `poll`_.  In order to conform to the
RIPE Atlas theme, it had to be named for an explorer, and so the winning
suggestion was for Magellan, *"in memory of those times when RTT was ~3 years"*.

.. |Documentation| image:: https://readthedocs.org/projects/ripe-atlas-tools/badge/?version=latest
  :target: http://ripe-atlas-tools.readthedocs.org/en/latest/?badge=latest
  :alt: Documentation Status
.. _ReadTheDocs: https://ripe-atlas-tools.readthedocs.org/
.. _guide: https://github.com/RIPE-NCC/ripe-atlas-tools/blob/master/CONTRIBUTING.rst
.. _poll: https://github.com/RIPE-NCC/ripe-atlas-tools/issues/13
.. |Build Status| image:: https://travis-ci.org/RIPE-NCC/ripe-atlas-tools.png?branch=master
   :target: https://travis-ci.org/RIPE-NCC/ripe-atlas-tools
.. |PYPI Version| image:: https://img.shields.io/pypi/v/ripe.atlas.tools.svg
.. |Python Versions| image:: https://img.shields.io/pypi/pyversions/ripe.atlas.tools.svg
.. |Python Implementations| image:: https://img.shields.io/pypi/implementation/ripe.atlas.tools.svg
.. |Python Format| image:: https://img.shields.io/pypi/format/ripe.atlas.tools.svg
.. |Requirements| image:: https://requires.io/github/RIPE-NCC/ripe-atlas-tools/requirements.svg?branch=master
  :target: https://requires.io/github/RIPE-NCC/ripe-atlas-tools/requirements/?branch=master
  :alt: Requirements Status

