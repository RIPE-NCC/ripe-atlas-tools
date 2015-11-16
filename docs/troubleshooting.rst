Troubleshooting
===============

Sometimes things don't go as planned.  In these cases, this page is here to
help.

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
