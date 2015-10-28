.. _requirements-and-installation:

Requirements & Installation
***************************

This is a Linux-based tool, though it should work just fine in a BSD variant.
Windows is definitely not supported.  In terms of the actual installation,
only Python's package manager (``pip``) is currently supported, and the
installation process may require some system packages to be installed in order
for everything to work.

System Requirements
===================

Some of the dependencies need to be compiled, so you'll need a compiler on your
system, as well as the development libraries for Python.  In the Linux world,
this typically means a few packages need to be installed from your standard
package manager, but in true Linux fashion, each distribution does things
slightly differently.

The most important thing to know is that you need Python 2.7 or 3. Python 2.6
will never be supported because it's old, ugly, and needs to die.

Distribution Specific Requirements
----------------------------------

Debian/Ubuntu
.............

The following has been tested on Debian Jessie.

Debian-based distributions require two system packages to be installed first:

.. code:: bash

    # apt-get install python-dev libffi-dev

You'll also need either ``virtualenv`` (recommended), or if you're not
comfortable with that, at the very least, you'll need ``pip``:

.. code:: bash

    # apt-get install python-virtualenv python-pip

CentOS
......

This following has been tested on CentOS 7.

Since we require Python's ``pip``, we first need to install the ``epel-release``
repository:

.. code:: bash

    # yum install epel-release

You'll also need the following system libraries:

.. code:: bash

    # yum install gcc libffi-devel openssl-devel

Once that's finished, you'll need access to ``virtualenv`` (recommended), or if
you're not comfortable with that, at the very least, you'll need ``pip``:

.. code:: bash

    # yum install python-virtualenv python-pip

Gentoo
......

If you're a Gentoo user, you never have to worry about development libraries,
but if you intend to use the bleeding-edge version of this package (and what
self-respecing Gentoo user wouldn't?) then you'll probably want to make sure
that git is built with curl support:

.. code:: bash

    # USE="curl" emerge git

If you're not going bleeding edge, or if you're just going to use SSH to get the
code from GitHub, then Gentoo will have everything ready for you.

Apple OSX
.........

Get a free copy of Xcode from the app store, and from there you should be good
to go.


.. _installation-python-requirements:

Python Requirements
===================

Importantly, Magellan requires Python 2.7 or higher.  For most desktop users,
this shouldn't be a problem, but for some older servers like CentOS 6 and lower,
this may cause some pain.  Thankfully, for most such systems, there are usually
work-arounds that allow you to install a more modern version of Python in
parallel.

Magellan depends on two other RIPE Atlas libraries, Cousteau and Sagan, which in
turn depend on a reasonable number of Python libraries.  Thankfully, Python's
package manager, ``pip`` should handle all of these for you:

* ripe.atlas.cousteau
* ripe.atlas.sagan
* tzlocal
* pyyaml


.. _installation:

Installation
============


.. _installation-from-pypi:

From PyPi
---------

Python's ``pip`` program can be used to install packages globally (not a good
idea since it conflicts with your system package manager) or on a per-user
basis.  Typically, this is done with `virtualenv`_, but if you don't want to use
that, you can always pass ``--user`` to the ``pip`` program and it'll install a
user-based copy in ``${HOME}/.local/``.

.. _virtualenv: https://pypi.python.org/pypi/virtualenv

.. code:: bash

    # From within a virtualenv
    $ pip install ripe.atlas.tools

    # In your user's local environment
    $ pip install --user ripe.atlas.tools

Or if you want to live on the edge and perhaps try submitting a pull request of
your own:

One day, we want this process to be as easy as installing any other command-line
program, that is, with ``apt``, ``dfn``, or ``emerge``, but until that day,
Python's standard package manager, ``pip`` does the job nicely.


.. _installation-from-github:

From GitHub
-----------

If you're feeling a little more daring and want to go bleeding-edge and use
our ``master`` branch on GitHub, you can have pip install right from there:::

    $ pip install git+https://github.com/RIPE-NCC/ripe.atlas.tools.git

If you think you'd like to contribute back to the project, we recommend the use
of pip's ``-e`` flag, which will place the Magellan code in a directory where
you can edit it, and see the results without having to go through a new install
procedure every time.  Simply clone the repo on GitHub and install it like so:::

    $ pip install -e git+https://github.com/your-username/ripe.atlas.tools.git


.. _installation-from-tarball:

From a Tarball
--------------

If for some reason you want to just download the source and install it manually,
you can always do that too.  Simply un-tar the file and run the following in the
same directory as ``setup.py``.::

    $ python setup.py install


.. _installation-troubleshooting:

Troubleshooting
===============

If you're using Mac OSX, the installation of Sagan, one of Magellan's
dependencies may give you trouble, especially in how Apple handles PyOpenSSL on
their machines.  Workarounds and proper fixes for this issue can be found in the
`Sagan installation documentation`_.

.. _Sagan installation documentation: https://ripe-atlas-sagan.readthedocs.org/en/latest/installation.html#troubleshooting
