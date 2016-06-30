Quickstart
==========

This is a very fast break down of everything you need to start using Ripe Atlas
on the command line.  Viewing public data is quick & easy, while creation is a
little more complicated, since you need to setup your authorisation key.

Viewing Public Data
-------------------

1. :ref:`Install <requirements-and-installation>` the toolkit.
2. View help with: ``ripe-atlas --help``
3. View a basic report for a public measurement: ``ripe-atlas report <measurement_id>``
4. View the live stream for a measurement: ``ripe-atlas stream <measurement_id>``
5. Get a list of probes in ASN 3333: ``ripe-atlas probe-search --asn 3333``
6. Get a list of measurements with the word "wikipedia" in them: ``ripe-atlas measurement-search --search wikipedia``

Creating a Measurement
----------------------

1. Log into `RIPE Atlas`_.  If you don't have an
   account, you can create one there for free.
2. Visit the `API Keys`_ page and create a new key
   with the permission ``Create a new user defined measurement``
3. Install the toolkit as below.
4. Configure the toolkit to use your key with ``ripe-atlas configure --set authorisation.create=MY_API_KEY``
5. View the help for measurement creation with ``ripe-atlas measure --help``
6. Create a measurement with ``ripe-atlas measure ping --target example.com``

.. _`RIPE Atlas`: https://atlas.ripe.net/
.. _`API Keys`: https://atlas.ripe.net/keys/

Advanced Use
------------

Refer to the :ref:`complete usage documentation <use>` for more advanced
options.
