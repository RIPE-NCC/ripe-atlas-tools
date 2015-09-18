ripe-atlas-tools
================

The official command-line client for RIPE Atlas.


Installation
------------

Currently, only Python's package manager (``pip``) is supported:

.. code:: bash

    $ pip install ripe.atlas.tools

Or if you want to live on the edge and perhaps try submitting a pull request of
your own:

.. code:: bash

    $ pip install git+github.com:RIPE-NCC/ripe-atlas-tools.git#egg=ripe.atlas.tools

Note that there are lots of dependencies that will automatically be drawn in and
installed at the moment, but we're going to try to scale that down.  Currently
only three packages are required, but they each have a lot of dependencies:

::

    ripe.atlas.cousteau
        python-dateutil
        socketIO-client
            websocket-client
                backports.ssl-match-hostname
    ripe.atlas.sagan
        IPy
        python-dateutil
        pytz
        pyOpenSSL
            cryptography
                idna
                pyasn1
                setuptools
                enum34
                ipaddress
                cffi>=0.8
                    pycparser
    tzlocal
        pytz
    pyyaml

In the future, we're going to make it easier to install though, with an eye on
integrating with end-user-friendly tools like ``apt``, ``rpm``, and ``emerge``.


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

Absolutely.  Pull requests are welcome, but give us a little time to get the
architecture settled first.
