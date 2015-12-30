.. _troubleshooting:

Troubleshooting
===============

Sometimes things don't go as planned.  In these cases, this page is here to
help.


.. _troubleshooting-insecureplatformwarning:

InsecurePlatformWarning
-----------------------

On older systems (running Python versions <2.7.10), you may be presented with a
warning message that looks like this::

    /path/to/lib/python2.7/site-packages/requests/packages/urllib3/util/ssl_.py:100:
    InsecurePlatformWarning: A true SSLContext object is not available. This
    prevents urllib3 from configuring SSL appropriately and may cause certain
    SSL connections to fail. For more information, see
    https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning.
      InsecurePlatformWarning

This is due to the insecure way older versions of Python handle secure
connections and a visit to the above URL will tell you that the fix is one of
three options:

* Upgrade to a modern version of Python
* Install three Python packages: ``pyopenssl``, ``ndg-httpsclient``, and
  ``pyasn1``
* `Suppress the warnings`_.  Don't do that though.

.. _Suppress the warnings: https://urllib3.readthedocs.org/en/latest/security.html#disabling-warnings


.. _troubleshooting-saganopensslosx:

Sagan, OpenSSL, and OSX
-----------------------

If you're using Mac OSX, the installation of Sagan, (one of Magellan's
dependencies) may give you trouble, especially in how Apple handles PyOpenSSL on
their machines.  Workarounds and proper fixes for this issue can be found in the
`Sagan installation documentation`_.

.. _Sagan installation documentation: https://ripe-atlas-sagan.readthedocs.org/en/latest/installation.html#troubleshooting


.. _troubleshooting-libyaml:

Complaints from libyaml
-----------------------

During the installation, you may see something like this scroll by:

    Running setup.py install for pyyaml
      checking if libyaml is compilable
      x86_64-linux-gnu-gcc -pthread -fno-strict-aliasing -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -fPIC -I/usr/include/python2.7 -c build/temp.linux-x86_64-2.7/check_libyaml.c -o build/temp.linux-x86_64-2.7/check_libyaml.o
      build/temp.linux-x86_64-2.7/check_libyaml.c:2:18: fatal error: yaml.h: No such file or directory
       #include <yaml.h>
                      ^
      compilation terminated.
    
      libyaml is not found or a compiler error: forcing --without-libyaml
      (if libyaml is installed correctly, you may need to
       specify the option --include-dirs or uncomment and
       modify the parameter include_dirs in setup.cfg)

Don't worry.  This is just the installation script noticing that you don't have
libyaml installed and it's complaining because it's good to have around for
performance reasons.  However, since we're only using YAML for configuration,
performance isn't an issue, and the fallback option will be sufficient.

If however, you don't like these sorts of errors, make sure that libyaml is
installed for your distribution before attempting to install this toolkit.
