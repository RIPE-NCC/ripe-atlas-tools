Release History
===============
2.3.0 (released 2018-11-23)
---------------------------

Features and changes
~~~~~~~~~~~~~~~~~~~~
- Add result date and time to traceroute, NTP and SSL renderers
- Add support for specifying measurement tags on measurement creation
- Add option (--go-web) to open measurement URL in browser
- Nicer presentation of 403 errors from the API
- Official supported Python versions changed to 2.7, 3.4, 3.5, 3.6 and 3.7

Bug Fixes
~~~~~~~~~
- Fix cousteau/sagan dependencies


2.2.3 (released 2017-01-17)
---------------------------

Bug Fixes
~~~~~~~~~
- Fix for distribution issues that prevented the command-line scripts from working

2.2.2 (released 2017-10-12)
---------------------------

Features and changes
~~~~~~~~~~~~~~~~~~~~
- Align various option defaults, minimums and maximums with API reality, including...
- ... allow the set of options necessary for "TCP ping" measurements https://labs.ripe.net/Members/wilhelm/measuring-your-web-server-reachability-with-tcp-ping 
- Add compact DNS results renderer
- Fix some unicode output issues

2.1 (released 2016-04-21)
---------------------------

New Features
~~~~~~~~~~~~
- Add a simple NTP renderer

Changes
~~~~~~~
- Use new cousteau (1.4) & sagan(1.2) versions.

Bug Fixes
~~~~~~~~~
- Fix for some unicode problems when using colors
- Fix issue #177, with `gdbm` problem.

2.0.2 (released 2016-10-21)
---------------------------

New Features
~~~~~~~~~~~~
- Add aliases to measurements IDs
- Add --traceroute-show-asns to traceroute renderer

Bug Fixes
~~~~~~~~~
- Stream command was not passing the correct API key. After API became stricter this command started failing.
- Handle missing geometry for probes.
- Fix issues for AS-paths with only 1 probe
- Various fixes for tests

2.0.1 (released 2016-04-20)
---------------------------

Changes
~~~~~~~
- Corrected references in the docs to obsolete command names.
- Fixed broken 2.0.0 egg.


2.0.0 (released 2016-04-20)
---------------------------

Changes
~~~~~~~
- Renamed and merged some commands for clarity, preserving the old names as deprecated aliases.
- Improved help text and usage output.
- Support for bash auto-completion.


1.2.3 (released 2016-03-08)
---------------------------

Changes
~~~~~~~
- Usage of newest Cousteau/Sagan library.
- Support of API keys for fetching results on report command.
- Default radius for probes filtering is changed to 15.
- Several changes for supporting Windows.


1.2.2 (released 2016-01-13)
---------------------------

New Features
~~~~~~~~~~~~
- Cleaner and more consistent implementation of the renderer plugable
  architecture.
- Usage of newest Cousteau library.


1.2.1 (released 2015-12-15)
---------------------------

Bug Fixes
~~~~~~~~~
- Restored some required template files.


1.2.0 (released 2015-12-15)
---------------------------

Output Changes
~~~~~~~~~~~~~~
- `#119`_: Support HTTP results.
- `#122`_: Allow packagers to set the user agent.


1.1.1 (released 2015-11-25)
---------------------------

Output Changes
~~~~~~~~~~~~~~
- `#103`_: Removed header from the ``report`` command.

Bug Fixes
~~~~~~~~~
- `#105`_: Measurement report and stream broken on Python3.4.

1.1.0 (released 2015-11-12)
---------------------------

New features
~~~~~~~~~~~~
- Support for the creation of NTP, SSLCert, and HTTP measurements.
- Additional argument in report command to filter results by probe ASN.
- Additional renderer that shows the different destination ASNs and some
  additional stats about them.

Bug Fixes
~~~~~~~~~
- Various fixes.

Changes
~~~~~~~
- Better testing.
- Additional documentation.

1.0.0 (released 2015-11-02)
---------------------------
- Initial release.

.. _#103: https://github.com/RIPE-NCC/ripe-atlas-tools/issues/103
.. _#105: https://github.com/RIPE-NCC/ripe-atlas-tools/issues/105
.. _#119: https://github.com/RIPE-NCC/ripe-atlas-tools/issues/119
.. _#122: https://github.com/RIPE-NCC/ripe-atlas-tools/issues/122
