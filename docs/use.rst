.. _use:

How to Use the RIPE Atlas Toolkit
*********************************

.. _use-configure:

Configuration
=============

For most features, Magellan will work out-of-the-box, but if you'd like to
customise the experience, or if you want to use this tool to create a
measurement of your own, then you'll need to configure it.

Thankfully, configuration is easy by way of the ``configure`` command:::

    $ ripe-atlas configure --help


.. _use-configure-options:

Options
-------

==================  =================   ========================================
Option              Arguments           Explanation
==================  =================   ========================================
``--editor``                            Invoke ${EDITOR} to edit the
                                        configuration directly

``--set``           path=value          Permanently set a configuration value so
                                        it can be used in the future.

``--init``                              Create a configuration file and save it
                                        into your home directory at:
                                        ``${HOME}/.config/ripe-atlas-tools/rc``
==================  =================   ========================================


.. _use-configure-examples:

Examples
--------

Create a standard configuration file.  Note that this typically isn't
necessary::

    $ ripe-atlas configure --init

Invoke your editor of choice to manually fiddle with the configuration file::

    $ ripe-atlas configure --editor

Set an arbitrary value within the configuration file.  You can use dot-separated
notation to dictation the value you wish to change::

    $ ripe-atlas configure --set authorisation.create=YOUR_API_KEY


.. _use-go:

Quick Measurement Information
=============================

For the impatient, and for those looking to see how they might write their own
plugins, we have a simple ``go`` command:::

    $ ripe-atlas go <measurement-id>

This will open a web browser and take you to the detail page for the measurement
id provided.


.. _use-measurements:

Measurement Querying
====================

A querying tool for finding existing measurements in the RIPE Atlas database.
You can request a table-formatted list of measurements based on search-string
lookups, type, start time, etc.


.. _use-measurements-options:

Options
-------

============================  ==================  ==============================
Option                        Arguments           Explanation
============================  ==================  ==============================
``--search``                  A free-form string  This could match the target or
                                                  description.

``--status``                  One of: scheduled,  The measurement status.
                              stopped, ongoing

``--af``                      One of: 4, 6        The address family.

``--type``                    One of: ping,       The measurement type.
                              traceroute, dns,
                              sslcert, ntp,
                              http

``--field``                   One of: status,     The field(s) to display.
                              target, url, type,  Invoke multiple times for
                              id, description     multiple fields. The default
                                                  is id, type, description, and
                                                  status.

``--ids-only``                                    Display a list of measurement
                                                  ids matching your filter
                                                  criteria.

``--limit``                   An integer          The number of measurements to
                                                  return.  The number must be
                                                  between 1 and 1000

``--started-before``          An ISO timestamp    Filter for measurements that
                                                  started before a specific
                                                  date. The format required is
                                                  YYYY-MM-DDTHH:MM:SS

``--started-after``           An ISO timestamp    Filter for measurements that
                                                  started after a specific date.
                                                  The format required is
                                                  YYYY-MM-DDTHH:MM:SS

``--stopped-before``          An ISO timestamp    Filter for measurements that
                                                  stopped before a specific
                                                  date. The format required is
                                                  YYYY-MM-DDTHH:MM:SS

``--stopped-after``           An ISO timestamp    Filter for measurements that
                                                  stopped after a specific date.
                                                  The format required is
                                                  YYYY-MM-DDTHH:MM:SS
============================  ==================  ==============================


.. _use-measurements-examples:

Examples
--------

Get a list of measurements::

    $ ripe-atlas measurement-search

Filter that list by ``status=ongoing``::

    $ ripe-atlas measurement-search --status ongoing

Further filter it by getting measurements that conform to IPv6::

    $ ripe-atlas measurement-search --status ongoing --af 6

Get that same list, but strip out everything but the measurement ids::

    $ ripe-atlas measurement-search --status ongoing --af 6 --ids-only

Limit that list to 200 entries::

    $ ripe-atlas measurement-search --status ongoing --af 6 --limit 200

Get that list, but show only the id, url and target fields:

    $ ripe-atlas measurement-search --status ongoing --af 6 \
      --field id --field url --field target

Filter for measurements of type ``dns`` that started after January 1, 2015::

    $ ripe-atlas measurement-search --type dns --started-after 2015-01-01


.. _use-probes:

Probe Querying
==============

Just like the ``measurement-search`` command, but for probes, and a lot more powerful.
You can use this command to find probes within an ASN, prefix, or geographical
region, and then aggregate by country, ASN, and/or prefix.


.. _use-probes-options:

Options
-------

============================  ==================  ==============================
Option                        Arguments           Explanation
============================  ==================  ==============================
``--limit``                   An integer          Return limited number of
                                                  probes.

``--field``                   One of: status,     The field(s) to display.
                              description,        Invoke multiple times for
                              address_v6,         multiple fields. The default
                              address_v4,         is id, asn_v4, asn_v6,
                              asn_v4, is_public,  country, and status.
                              asn_v6, id,
                              prefix_v4,
                              prefix_v6,
                              is_anchor,
                              country,
                              coordinates

``--aggregate-by``            country, asn_v4,    Aggregate list of probes based
                              asn_v6,             on all specified aggregations.
                              prefix_v4,          Multiple aggregations
                              prefix_v6           supported.

``--all``                                         Fetch *ALL* probes. That will
                                                  give you a loooong list.

``--max-per-aggregation``     An integer          Maximum number of probes per
                                                  aggregated bucket.

``--ids-only``                                    Print only IDs of probes.
                                                  Useful to pipe it to another
                                                  command.

``--asn``                     An integer          Filter the list by an ASN

``--asnv4``                   An integer          Filter the list by an ASN

``--asnv6``                   An integer          Filter the list by an ASN

``--prefix``                  A prefix string     Filter the list by a prefix

``--prefixv4``                A prefix string     Filter the list by a prefix

``--prefixv6``                A prefix string     Filter the list by a prefix

``--location``                A free-form string  The location of probes as a
                                                  string i.e. 'Amsterdam'

``--center``                  A pair of           Location as
                              geographic          <lat>,<lon>-string, i.e.
                              coordinates         "48.45,9.16"

``--radius``                  An integer          Radius in km from specified
                                                  center/point.

``--country``                 A two-letter        The country in which the
                              ISO country code    probes are located.
============================  ==================  ==============================


.. _use-probes-examples:

Examples
--------

Get a list of probes within ASN 3333::

    $ ripe-atlas probe-search --asn 3333

Further filter that list to show only probes in ASN 3333 from the Netherlands::

    $ ripe-atlas probe-search --asn 3333 --country nl

Change the limit from the default of 25 to 200::

    $ ripe-atlas probe-search --asn 3333 --limit 200

Aggregate the probes by country, and then by ASN::

    $ ripe-atlas probe-search --asn 3333 --aggregate-by country --aggregate-by asn

Show the id, url, target, description, and whether the probe is public or not::

    $ ripe-atlas probe-search --asn 3333 --field id --field url --field description \
      --field is_public


.. _use-report:

Result Reporting
================

A means to generate a simple text-based report based on the results from a
measurement.  Typically, this is used to get the latest results of a measurement
in a human-readable format, but with the ``--start-time`` and ``--stop-time``
options, you can get results from any time range you like. It's possible to generate the report by automatically fetching the results from the API, by reading a local file, or by reading standard input.


.. _use-report-options:

Options
-------

==================  ==================  ========================================
Option              Arguments           Explanation
==================  ==================  ========================================
``--auth``          RIPE Atlas key      One of the RIPE Atlas key alias
                    alias               configured for results fetching.

``--probes``        A comma-separated   Limit the report to only results
                    list of probe ids   obtained from specific probes.

``--probe-asns``    A comma-separated   Limit the report to only results
                    list of ASNs        obtained from probes belonging to
                                        specific ASNs.

``--renderer``      One of: dns, http,  The renderer you want to use. If this
                    ntp, ping, raw,     isn't defined, an appropriate renderer
                    ssl_consistency,    will be selected.
                    sslcert,
                    traceroute,
                    traceroute_aspath,
                    aggregate_ping

``--from-file``     A file path         The source of the data to be
                                        rendered. Conflicts with
                                        specifying a measurement_id to
                                        fetch from the API.

``--aggregate-by``  One of: status,     Tell the rendering engine to aggregate
                    prefix_v4,          the results by the selected option. Note
                    prefix_v6,          that if you opt for aggregation, no
                    country,            output will be generated until all
                    rtt-median,         results are received.
                    asn_v4, asn_v6

``--start-time``    An ISO timestamp    The start time of the report. The format
                                        should conform to YYYY-MM-DDTHH:MM:SS

``--stop-time``     An ISO timestamp    The stop time of the report. The format
                                        should conform to YYYY-MM-DDTHH:MM:SS
==================  ==================  ========================================


.. _use-report-examples:

Examples
--------

Get the latest results of measurement 1001::

    $ ripe-atlas report 1001

The same, but specifically request the ping renderer::

    $ ripe-atlas report 1001 --renderer ping

Aggregate those results by country::

    $ ripe-atlas report 1001 --aggregate-by country

Get results from the same measurement, but show all results from the first week
of 2015::

    $ ripe-atlas report 1001 --start-time 2015-01-01 --stop-time 2015-01-07

Get results from the first day of 2015 until right now::

    $ ripe-atlas report 1001 --start-time 2015-01-01

Pipe the contents of an arbitrary file into the renderer.  The rendering
engine will be guessed from the first line of input::

    $ cat /path/to/file/full/of/results | ripe-atlas report

The same, but point Magellan to a file deliberately rather than using a pipe::

    $ ripe-atlas report --from-file /path/to/file/full/of/results


.. _use-stream:

Result Streaming
================

Connect to the streaming API and render the results in real-time as they come
in.

.. _use-stream-options:

Options
-------

==================  ==================  ========================================
Option              Arguments           Explanation
==================  ==================  ========================================
``--auth``          RIPE Atlas key      One of the RIPE Atlas key alias
                    alias               configured for results fetching.

``--limit``         A number < 1000     The maximum number of results you want
                                        to stream.  The default is to stream
                                        forever until you hit ``Ctrl+C``.

``--renderer``      One of: dns, http,  The renderer you want to use. If this
                    ntp, ping, raw,     isn't defined, an appropriate renderer
                    ssl_consistency,    will be selected.
                    sslcert,
                    traceroute,
                    traceroute_aspath,
                    aggregate_ping
==================  ==================  ========================================


.. _use-stream-examples:

Examples
--------

Stream the results from measurement #1001::

    $ ripe-atlas stream 1001

Limit those results to 500::

    $ ripe-atlas stream 1001 --limit 500

Specify a renderer::

    $ ripe-atlas stream 1001 --renderer ping

Combine for fun and profit::

    $ ripe-atlas stream 1001 --renderer ping --limit 500


.. _use-measure:

Measurement Creation
====================

The most complicated command we have, this will create a measurement (given a
plethora of options) and begin streaming the results back to you in a
standardised rendered form.

It's invoked by using a special positional argument that dictates the type of
measurement you want to create.  This also unlocks special options, specific to
that type.  See the :ref:`examples <use-measure-examples>` for more information.


.. _use-measure-options:

Options
-------

All measurements share a base set of options.

======================  ==================  ====================================
Option                  Arguments           Explanation
======================  ==================  ====================================
``--renderer``          One of: dns, http,  The renderer you want to use. If
                        ntp, ping, raw,     this isn't defined, an appropriate
                        ssl_consistency,    renderer will be selected.
                        sslcert,
                        traceroute,
                        traceroute_aspath,
                        aggregate_ping

``--dry-run``                               Do not create the measurement, only
                                            show its definition.

``--auth``              An API key          The API key you want to use to
                                            create the measurement.

``--af``                One of: 4, 6        The address family, either 4 or 6.
                                            The default is a guess based on the
                                            target, favouring 6.

``--description``       A free-form string  The description/name of your new
                                            measurement.

``--target``            A domain or IP      The target, either a domain name or
                                            IP address. If creating a DNS
                                            measurement, the absence of this
                                            option will imply that you wish to
                                            use the probe's resolver.

``--no-report``                             Don't wait for a response from the
                                            measurement, just return the URL at
                                            which you can later get information
                                            about the measurement.

``--go-web``                                Don't wait for a response from the
                                            measurement, just immediately open the measurement URL in the default web browser.

``--resolve-on-probe``                      Flag that indicates that a name
                                            should be resolved (using DNS) on
                                            the probe. Otherwise it will be
                                            resolved on the RIPE Atlas servers.

``--interval``          An integer          Rather than run this measurement as
                                            a one-off (the default), create this
                                            measurement as a recurring one, with
                                            an interval of n seconds between
                                            attempted measurements. This option
                                            implies ``--no-report``.

``--from-area``         One of: WW, West,   The area from which you'd like to
                        North-Central,      select your probes.
                        South-Central,
                        North-East,
                        South-East

``--from-country``      A two-letter ISO    The country from which you'd like to
                        country code        select your probes.

``--from-prefix``       A prefix string     The prefix from which you'd like to
                                            select your probes.

``--from-asn``          An ASN number       The ASN from which you'd like to
                                            select your probes.

``--from-probes``       A comma-separated   Probes you want to use in your
                        list of probe ids   measurement.

``--from-measurement``  A measurement id    A measurement id which you want to
                                            use as the basis for probe selection
                                            in your new measurement.  This is a
                                            handy way to re-create a measurement
                                            under conditions similar to another
                                            measurement.

``--probes``            An integer          The number of probes you want to
                                            use.

``--include-tag``       A tag name          Include only probes that are marked
                                            with this tag.  Note that this
                                            option may be repeated.

``--exclude-tag``       A tag name          Exclude probes that are marked with
                                            this tag. Note that this option may
                                            be repeated.
``--measurement-tags``  A comma-separated   Measurement tags to be applied to
                        list of             the newly created measurement.
                        measurement tags
======================  ==================  ====================================

.. _use-measure-options-ping:

Ping-Specific Options
:::::::::::::::::::::

======================  ==================  ====================================
Option                  Arguments           Explanation
======================  ==================  ====================================
``--packets``           An integer          The number of packets sent

``--size``              An integer          The size of packets sent

``--packet-interval``   An integer
======================  ==================  ====================================

.. _use-measure-options-traceroute:

Traceroute-Specific Options
:::::::::::::::::::::::::::

=============================  ==================  ====================================
Option                         Arguments           Explanation
=============================  ==================  ====================================
``--packets``                  An integer          The number of packets sent

``--size``                     An integer          The size of packets sent

``--protocol``                 One of: ICMP, UDP,  The protocol used.  For DNS
                               TCP                 measurements, this is limited to UDP
                                                   and TCP, but traceroutes may use
                                                   ICMP as well.

``--timeout``                  An integer          The timeout per-packet

``--dont-fragment``                                Don't Fragment the packet

``--paris``                    An integer          Use Paris. Value must be
                                                   between 0 and 64.If 0, a
                                                   standard traceroute will be
                                                   performed.

``--first-hop``                An integer          Value must be between 1 and
                                                   255.

``--max-hops``                 An integer          Value must be between 1 and
                                                   255.

``--port``                     An integer          Destination port, valid for
                                                   TCP only.

``--destination-option-size``  An integer          IPv6 destination option
                                                   header.

``--hop-by-hop-option-size``   An integer          IPv6 hop by hop option header.
=============================  ==================  ====================================


.. _use-measure-options-dns:

DNS-Specific Options
::::::::::::::::::::

============================  ==================  ==============================
Option                        Arguments           Explanation
============================  ==================  ==============================
``--query-class``             One of: IN, CHAOS   The query class.  The default
                                                  is "IN"

``--query-type``              One of: A, SOA,     The query type.  The default
                              TXT, SRV, SSHFP,    is "A"
                              TLSA, NSEC, DS,
                              AAAA, CNAME,
                              DNSKEY, NSEC3,
                              PTR, HINFO,
                              NSEC3PARAM, NS,
                              MX, RRSIG, ANY

``--query-argument``          A string            The DNS label to query.

``--set-cd-bit``                                  Set the DNSSEC Checking
                                                  Disabled flag (RFC4035)

``--set-do-bit``                                  Set the DNSSEC OK flag
                                                  (RFC3225)

``--set-nsid-bit``                                Include an EDNS name server.
                                                  ID request with the query.

``--udp-payload-size``        An integer          May be any integer between 512
                                                  and 4096 inclusive.

``--set-rd-bit``                                  Set the Recursion Desired
                                                  flag.

``--retry``                   An integer          Number of times to retry.
============================  ==================  ==============================


.. _use-measure-options-sslcert:

SSL Certificate-Specific Options
::::::::::::::::::::::::::::::::

============================  ==================  ==============================
Option                        Arguments           Explanation
============================  ==================  ==============================
``--port``                    An integer          The port to query
============================  ==================  ==============================


.. _use-measure-options-http:

HTTP-Specific Options
:::::::::::::::::::::

============================  ==================  ==============================
Option                        Arguments           Explanation
============================  ==================  ==============================
``--header-bytes``            An integer          The maximum number of bytes to
                                                  retrieve from the header
``--version``                 A string            The HTTP version to use
``--method``                  A string            The HTTP method to use
``--path``                    A string            The path on the webserver
``--query-string``            A string            An arbitrary query string
``--user-agent``              A string            An arbitrary user agent
``--body-bytes``              An integer          The maximum number of bytes to
                                                  retrieve from the body
``--timing-verbosity``        One of: 0, 1, 2     The amount of timing
                                                  information you want returned.
                                                  1 returns the time to read, to
                                                  connect, and to first byte, 2
                                                  returns timing information per
                                                  read system call.  0 (default)
                                                  returns no additional timing
                                                  information.
============================  ==================  ==============================


.. _use-measure-options-ntp:

NTP-Specific Options
::::::::::::::::::::

============================  ==================  ==============================
Option                        Arguments           Explanation
============================  ==================  ==============================
``--packets``                 An integer          The number of packets sent
``--timeout``                 An integer          The timeout per-packet
============================  ==================  ==============================


.. _use-measure-examples:

Examples
--------

The simplest of measurements.  Create a ping with 50 probes to example.com::

    $ ripe-atlas measure ping --target example.com

The same, but don't actually create it, just show what would be done::

    $ ripe-atlas measure ping --target example.com --dry-run

Be more specific about which address family you want to target::

    $ ripe-atlas measure ping --target example.com --af 6

Ask for 20 probes from Canada::

    $ ripe-atlas measure ping --target example.com --probes 20 --from-country ca

Or ask for 20 Canadian probes that definitely support IPv6::

    $ ripe-atlas measure ping --target example.com --probes 20 \
      --from-country ca --include-tag system-ipv6-works

Rather than creating a one-off create a recurring measurement::

    $ ripe-atlas measure ping --target example.com --interval 3600

Moving onto DNS measurements, do a lookup for example.com.  Since we're not
specifying ``--target`` here, this implies that we want to use the probe's
resolver::

    $ ripe-atlas measure dns --query-argument example.com

Getting a little more complicated, let's set a few special bits and make a more
complex query::

    $ ripe-atlas measure dns --query-type AAAA --query-argument example.com \
      --set-nsid-bit --set-rd-bit --set-do-bit --set-cd-bit


.. _use-shortcuts:

Shortcuts
---------

If you're creating a lot of measurements in a short time, typing out
``ripe-atlas measure traceroute`` a whole bunch of times can be tiresome, so
we've added a few shortcut scripts for you:

=================================  ==========================
Where you'd typically write        You could use this instead
=================================  ==========================
``ripe-atlas measure ping``        ``aping``
``ripe-atlas measure traceroute``  ``atraceroute``
``ripe-atlas measure dns``         ``adig``
``ripe-atlas measure sslcert``     ``asslcert``
``ripe-atlas measure http``        ``ahttp``
``ripe-atlas measure ntp``         ``antp``
=================================  ==========================

So for example, these two commands are the same::

    $ ripe-atlas measure ping --target example.com
    $ aping --target example.com

If you want to streamline your typing process even more than this, we recommend
the use of your shell's ``alias`` feature, which is both powerful and
customisable for your needs.
