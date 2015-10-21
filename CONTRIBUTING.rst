How To Contribute
=================

We would love to have contributions from everyone. No contribution is too small; please submit as many fixes for typos and grammar bloopers as you can!

To make participation in this project as pleasant as possible for everyone, we adhere to the `Code of Conduct`_ by the Python Software Foundation.

The following steps will help you get started:

Fork, then clone the repo:
::

    git clone git@github.com:your-username/ripe-atlas-tools.git

Make sure the tests pass beforehand:
::

    tox

or

::

    nosetests tests/

Make your changes. Add tests for your change. Make the tests pass:
::

    tox

or

::

    nosetests tests/

Push to your fork and `submit a pull request`_.

Here are a few guidelines that will increase the chances of a quick merge of your pull request:

- *Always* try to add tests and docs for your code. If a feature is tested and documented, it's easier for us to merge it.
- Follow `PEP 8`_.
- Write `good commit messages`_.
- If you change something that is noteworthy, don't forget to add an entry to the changes_.

.. note::
   - If you think you have a great contribution but aren’t sure whether it adheres -- or even can adhere -- to the rules: **please submit a pull request anyway**! In the best case, we can transform it into something mergable, in the worst case the pull request gets politely closed. There’s absolutely nothing to fear.
   - If you have a great idea but you don't know how or you don't have time to implement it, please consider opening an issue and someone will pick it up as soon as it's possible.


Thank you for considering to contribute to our tool!
If you have any question or concerns, feel free to reach out the RIPE Atlas team.


.. _`submit a pull request`:  https://github.com/RIPE-NCC/ripe-atlas-tools/compare/
.. _`PEP 8`: https://www.python.org/dev/peps/pep-0008/
.. _`good commit messages`: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
.. _`Code of Conduct`: https://www.python.org/psf/codeofconduct/
.. _changes: https://github.com/RIPE-NCC/ripe-atlas-tools/blob/master/CHANGES.rst
