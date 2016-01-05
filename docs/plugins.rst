.. _plugins:

How to Create Your Own Plugins
==============================

We built this toolkit for the community, and we knew going in that we couldn't
possibly build every feature that every user could want, so we built this
thing to be pluggable.  You can write your own renderer(s) and use them
seamlessly within your own environment, and if you think that others might
benefit from your work, you can share your renderer as easy as posting a file
online.

Ready?

So you have an idea now.  You want to create a renderer called "awesomerenderer"
and you want it to do some fancy things with traceroute measurement results.
What do you have to do?


.. _plugins-create:

Create Your Renderer File
-------------------------

As we've already covered, Magellan will look for renderers in very specific
places, so you need to put your file(s) there.  Additionally however, you have
to make sure that you conform to Python norms, or stuff just won't work.  Here's
the basic commands to get you started:

.. code:: bash

    $ mkdir -p ${HOME}/.config/ripe-atlas-tools/renderers
    $ touch ${HOME}/.config/ripe-atlas-tools/renderers/__init__.py
    $ touch ${HOME}/.config/ripe-atlas-tools/renderers/my_renderer.py

The ``mkdir`` step there will create the renderers directory (if it doesn't
exist already), and the ``touch`` commands will create the mandatory init file
(for Python) and your renderer.  Note that you can use whatever name you like
for your renderer, so long as it consists only of letters, numbers, and the
underscore and that it starts with a letter.  Also, to be compliant with the
rest of the project, it should be entirely lowercase.  For our purposes though,
``my_renderer.py`` will suffice.


.. _plugins-try-to-run:

(Try to) Run It!
----------------

If you run this right now:

.. code:: bash

    $ ripe-atlas report --help

You should see ``my_renderer`` int he list of options for ``--renderer``.
Pretty cool eh?  However, if you try to run that, this'll happen:

.. code:: bash

    $ ripe-atlas report 1000192 --renderer my_renderer
    The renderer you selected, "my_renderer" could not be found.

Which kind of makes sense really.  You've created a file called ``my_renderer``,
but it's totally empty.  Magellan found the file alright, but when it tried to
import ``Renderer`` from it, everything exploded.


.. _plugins-write:

Actually Write a Renderer
-------------------------

So now you know that we can see your renderer file, but you need to know what
kind of code to put in there.  Don't worry, we've got you covered:


.. _plugins-write-anatomy:

Anatomy of a Renderer
~~~~~~~~~~~~~~~~~~~~~

A "renderer" is simply a file located in a special place that contains some
Python code defining a class called ``Renderer`` that subclasses
``ripe.atlas.tools.renderers.base.BaseRenderer``.

Your class need only define one method: ``on_result()``, which is called every
time a new result comes down the pipe.  Let's look at a really simple example:

.. code:: python

    from ripe.atlas.tools.renderers.base import Renderer as BaseRenderer


    class Renderer(BaseRenderer):

        # This renderer is capable of handling ping results only.
        RENDERS = [BaseRenderer.TYPE_PING]

        def on_result(self, result):
            """
            on_result() only gets one argument, a result object, which is
            actually an instance of a RIPE Atlas result parsed with Sagan:
              https://ripe-atlas-sagan.readthedocs.org/
            """

            return "Packets received: {}".format(result.packets_received)

As you can see, this renderer isn't very useful, but we're providing it here to
give you a rough idea of what you get to play with when defining your own
renderer.

In the case of our PingPacketRenderer, we're doing the simplest of tasks: we're
returning the number of packets in each result.  The job of ``on_result()`` is
to take a Sagan result object as input and return a string.  **It should not
print anything to standard out**, rather it should simply return a string that
will get printed to standard out by the surrounding framework.


.. _plugins-write-anatomy-additional:

Additional Options
::::::::::::::::::

It's likely that you will only ever need to work with ``on_result()``, but in
the event that you'd like to get more complicated, there are options:
``header()``, ``additional()``, and ``footer()``.  Note however that these other
methods are currently only available to the ``report`` command.  Streaming only
makes use of ``on_result()``.


.. _plugins-write-anatomy-additional-header:

header()
........

The value returned from this method is printed to standard out before any
results are captured.  By default it returns an empty string.


.. _plugins-write-anatomy-additional-additional:

additional()
............

Typically used for summary logic, this is executed after the last result is
rendered.  A common pattern is to override ``__init__()`` to set some collector
properties, update them via ``on_result()``, and then print out said properties
in a summary via this method.  For an example, let's update our ``Renderer``
class:

.. code:: python

    from ripe.atlas.tools.renderers.base import Renderer as BaseRenderer


    class Renderer(BaseRenderer):

        RENDERS = [BaseRenderer.TYPE_PING]

        def __init__(self, *args, **kwargs):
            self.packet_total = 0
            BaseRenderer.__init__(self, *args, **kwargs)

        def on_result(self, result):
            self.packet_total += result.packets_received
            return "Packets received: {}\n".format(result.packets_received)

        def additional(self, results):
            return "\nTotal packets received: {}\n".format(self.packet_total)

Note that the passed-in value of ``results`` is the list of Sagan Result objects
that were previously looped over for on_result().  You can do some interesting
things with that.


.. _plugins-write-anatomy-additional-footer:

footer()
........

Much the same as ``header()``, this should return a string, but unlike
``header()``, the output of this method is rendered after everything else.


.. _plugins-run:

Run It!
-------

Now that you've written your renderer and the file is stored where it's supposed
to be, it should be ready to go:

.. code:: bash

    $ ripe-atlas report --help

You should see ``my_renderer`` in the list of options for ``--renderer`` just as
before, but now when you actually try to execute it...

.. code:: bash

    $ ripe-atlas report 1000192 --renderer my_renderer
    Packets received: 3
    Packets received: 3
    Packets received: 3
    Packets received: 3
    Packets received: 3
    Packets received: 3

    Total packets received: 18

It's not very interesting, but it's a start!


.. _plugins-contributing:

Contributing
------------

We love it when people write stuff that talks to our stuff.  If you think your
stuff is useful, it'd be awesome if you could do any of these:

* Post to the [ripe-atlas mailing list](https://www.ripe.net/mailman/listinfo/ripe-atlas)
  about it.  You can also solicit feedback from the RIPE Atlas developers or the
  wider community on this list.
* Write a blog post about your plugin, what makes it useful, etc.
* Tweet about it.  Feel free to mention [@RIPE_Atlas](https://twitter.com/ripe_atlas)
  and we might even retweet it.
* Create a [pull request](https://github.com/RIPE-NCC/ripe-atlas-tools/pulls)
  for this project to get your plugin added to core.
