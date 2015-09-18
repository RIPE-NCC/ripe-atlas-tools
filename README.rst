ripe-atlas-tools
================

The official command-line client for RIPE Atlas.


Disclaimer
----------

All of this is super-beta.  If it breaks, you get to keep all the shiny pieces.


Quickstart
----------

This is a very fast break down of everything you need to start using Ripe Atlas
on the command line.  Viewing public data is quick & easy, while creation is a
little more complicated, since you need to setup your authorisation key.

Viewing Public Data
:::::::::::::::::::

1. Install the toolkit as below.
2. View help with: ``ripe-atlas --help``
3. View a basic report for a public measurement ``ripe-atlas report <measurement_id>``
4. View the live stream for a measurement ``ripe-atlas stream <measurement_id>``

Creating a Measurement
::::::::::::::::::::::

1. Log into [RIPE Atlas](https://atlas.ripe.net/).  If you don't have an
   account, you can create one there for free.
2. Visit the [API Keys](https://atlas.ripe.net/keys/) page and create a new key
   with the permission ``Create a new user defined measurement``
3. Install the toolkit as below.
4. Configure the toolkit to use your key with ``ripe-atlas configure --set authorisation.create=MY_API_KEY``
5. View the help for measurement creation with ``ripe-atlas measure --help``
5. Create a measurement with ``ripe-atlas measure ping --target example.com``


Installation
------------

Currently, only Python's package manager (``pip``) is supported:

.. code:: bash

    $ pip install ripe.atlas.tools

Or if you want to live on the edge and perhaps try submitting a pull request of
your own:

.. code:: bash

    $ pip install -e git+github.com:RIPE-NCC/ripe-atlas-tools.git#egg=ripe.atlas.tools

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
