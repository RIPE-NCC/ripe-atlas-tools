How To Contribute
=================

We would love to have contributions from everyone and no contribution is too
small.  Please submit as many fixes for typos and grammar bloopers as you can!

To make participation in this project as pleasant as possible for everyone,
we adhere to the `Code of Conduct`_ by the Python Software Foundation.

The following steps will help you get started:

Fork, then clone the repo:

.. code:: bash

    $ git clone git@github.com:your-username/ripe-atlas-tools.git

Make sure the tests pass beforehand:

.. code:: bash

    $ tox

or

.. code:: bash

    $ nosetests tests/

Make your changes. Include tests for your change. Make the tests pass:

.. code:: bash

    $ tox

or

.. code:: bash

    $ nosetests tests/

Push to your fork and `submit a pull request`_.

Here are a few guidelines that will increase the chances of a quick merge of
your pull request:

- *Always* try to add tests and docs for your code. If a feature is tested and
  documented, it's easier for us to merge it.
- Follow `PEP 8`_.
- Write `good commit messages`_.
- If you change something that is noteworthy, don't forget to add an entry to
  the `changes`_.

.. note::
   - If you think you have a great contribution but aren’t sure whether it
     adheres -- or even can adhere -- to the rules: **please submit a pull
     request anyway**! In the best case, we can transform it into something
     usable, in the worst case the pull request gets politely closed. There’s
     absolutely nothing to fear.
   - If you have a great idea but you don't know how or don't have the time to
     implement it, please consider opening an issue and someone will pick it up
     as soon as possible.

Thank you for considering a contribution to this project!  If you have any
questions or concerns, feel free to reach out the RIPE Atlas team via the
`mailing list`_, `GitHub Issue Queue`_, or `messenger pigeon`_ -- if you must.

.. _submit a pull request:  https://github.com/RIPE-NCC/ripe-atlas-tools/compare/
.. _PEP 8: https://www.python.org/dev/peps/pep-0008/
.. _good commit messages: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
.. _Code of Conduct: https://www.python.org/psf/codeofconduct/
.. _changes: https://github.com/RIPE-NCC/ripe-atlas-tools/blob/master/CHANGES.rst
.. _mailing list: https://www.ripe.net/mailman/listinfo/ripe-atlas
.. _GitHub Issue Queue: https://github.com/RIPE-NCC/ripe-atlas-tools/issues
.. _messenger pigeon: https://tools.ietf.org/html/rfc1149
