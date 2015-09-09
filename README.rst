ripe-atlas
==========

The Official command-line client for RIPE Atlas.


Installation
------------

Currently, only Python's package manager (``pip``) is supported, and even that
must point to this git repo for anything to work:

    $ pip install git+github.com:RIPE-NCC/ripe-atlas-tools.git#egg=ripe.atlas.tools

Note that there are lots of dependencies that will automatically be drawn in and
installed at the moment, but we're going to try to scale that down:

* arrow
* backports.ssl-match-hostname
* cffi
* cryptography
* enum34
* idna
* ipaddress
* IPy
* pyasn1
* pycparser
* pyOpenSSL
* python-dateutil
* pytz
* requests
* ripe.atlas.cousteau
* ripe.atlas.sagan
* ripe.atlas.tools
* setuptools
* six
* socketIO-client
* ujson
* websocket-client

In the future, we're going to make it easier to install though, with an eye on
integrating with end-user-friendly tools like ``apt``, ``rpm``, and ``emerge``.


How Does it Work?
-----------------

Presently, the setup is pretty crude.  You can create a ping or traceroute
measurement with limited options from the command line:

    $ ripe-atlas measure ping --target example.com
    $ ripe-atlas measure ping --packets 7 --size 42 --target example.com
    $ ripe-atlas measure traceroute --target example.com
    $ ripe-atlas measure traceroute --packets 2 --target example.com

This will create a one-off measurement and then wait for the results to roll in,
formatting them as they do.

You can also use it to connect to a stream of formatted data.  This command will
start streaming out all of the results from one of our oldest measurements:

    $ ripe-atlas stream 1001

Or you can generate a simple report:

    $ ripe-atlas report 1001

Configuration is done by way of a config file, and modifying it can be done from
the command line:

    ripe-atlas configure --set authorisation.create=MY_API_KEY


Can I Contribute?
-----------------

Absolutely.  Pull requests are welcome, but give us a little time to get the
architecture settled first.
