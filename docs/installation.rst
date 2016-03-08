.. _requirements-and-installation:

Requirements & Installation
***************************

This is a Linux-based tool, though it should work just fine in a BSD variant.
Windows is experimentally supported.  In terms of the actual installation,
only Python's package manager (``pip``) is currently supported, and the
installation process may require some system packages to be installed in order
for everything to work.


.. _requirements-and-installation-system-requirements:

System Requirements
===================

Some of the dependencies need to be compiled, so you'll need a compiler on your
system, as well as the development libraries for Python.  In the Linux world,
this typically means a few packages need to be installed from your standard
package manager, but in true Linux fashion, each distribution does things
slightly differently.

The most important thing to know is that you need Python 2.7 or 3. Python 2.6
will never be supported because it's old, ugly, and needs to die.


.. _requirements-and-installation-distribution-specific-requirements:

Distribution Specific Requirements
----------------------------------

.. note::

    If you're running OpenBSD, you can skip this whole section.  You can even
    skip the next one too.  Just skip down to
    :ref:`Installation:OpenBSD <installation-from-openbsd>` and follow the
    instructions.  Everything else is taken care of for you.


.. _requirements-and-installation-distribution-specific-requirements-debian:

Debian/Ubuntu
.............

The following has been tested on Debian Jessie.

Debian-based distributions require three system packages to be installed first:

.. code:: bash

    sudo apt-get install python-dev libffi-dev libssl-dev

You'll also need either ``virtualenv`` (recommended), or if you're not
comfortable with that, at the very least, you'll need ``pip``:

.. code:: bash

    sudo apt-get install python-virtualenv python-pip


.. _requirements-and-installation-distribution-specific-requirements-centos:

CentOS
......

This following has been tested on CentOS 7.

Since we require Python's ``pip``, we first need to install the ``epel-release``
repository:

.. code:: bash

    sudo yum install epel-release

You'll also need the following system libraries:

.. code:: bash

    sudo yum install gcc libffi-devel openssl-devel

Once that's finished, you'll need access to ``virtualenv`` (recommended), or if
you're not comfortable with that, at the very least, you'll need ``pip``:

.. code:: bash

    sudo yum install python-virtualenv python-pip


.. _requirements-and-installation-distribution-specific-requirements-gentoo:

Gentoo
......

If you're a Gentoo user, you never have to worry about development libraries,
but if you intend to use the bleeding-edge version of this package (and what
self-respecting Gentoo user wouldn't?) then you'll probably want to make sure
that git is built with curl support:

.. code:: bash

    sudo USE="curl" emerge git

If you're not going bleeding edge, or if you're just going to use SSH to get the
code from GitHub, then Gentoo will have everything ready for you.


.. _requirements-and-installation-distribution-specific-requirements-apple:

Apple OSX
.........

These instructions expect that you've got Python's ``pip`` installed, so if you
have no idea what that is, or simply don't have it yet, you should be able to
install pip with one easy command:

.. code:: bash

    sudo easy_install pip

Outside of that, a few of the Python dependencies require that you have a
compiler on your system.  For this, you need only get a free copy of `Xcode`_
from the app store, and from there you should be good to go.

.. _Xcode: https://itunes.apple.com/us/app/xcode/id497799835


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


.. _installation-from-openbsd:

OpenBSD
-------

OpenBSD was the first platform to have a port for Magellan, so installation is
easy:

.. code:: bash

    sudo pkg_add py-ripe.atlas.tools


.. _installation-from-freebsd:

FreeBSD
-------

FreeBSD has a port ready for you:

.. code:: bash

cd /usr/ports/net/py-ripe.atlas.tools
make install


.. _installation-from-gentoo:

Gentoo
------

There's an ebuild for Magellan in Portage, so installation is as any other
package:

.. code:: bash

    sudo emerge ripe-atlas-tools


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
    pip install ripe.atlas.tools

    # In your user's local environment
    pip install --user ripe.atlas.tools

Or if you want to live on the edge and perhaps try submitting a pull request of
your own:

One day, we want this process to be as easy as installing any other command-line
program, that is, with ``apt``, ``dfn``, or ``emerge``, but until that day,
Python's standard package manager, ``pip`` does the job nicely.


.. _installation-from-github:

From GitHub
-----------

If you're feeling a little more daring and want to go bleeding-edge and use
our ``master`` branch on GitHub, you can have pip install right from there:

.. code:: bash

    pip install git+https://github.com/RIPE-NCC/ripe-atlas-tools.git

If you think you'd like to contribute back to the project, we recommend the use
of pip's ``-e`` flag, which will place the Magellan code in a directory where
you can edit it, and see the results without having to go through a new install
procedure every time.  Simply clone the repo on GitHub and install it like so:

.. code:: bash

    pip install -e git+https://github.com/your-username/ripe-atlas-tools.git


.. _installation-from-tarball:

From a Tarball
--------------

If for some reason you want to just download the source and install it manually,
you can always do that too.  Simply un-tar the file and run the following in the
same directory as ``setup.py``:

.. code:: bash

    python setup.py install
