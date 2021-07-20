
.. highlight:: console

thorcam's documentation
=========================

This is the Sphinx documentation for the SDSS Python product ``thorcam``. This documentation is for version |thorcam_version|.


Getting started
---------------

``thorcam`` is a wrapper around the `libfli <https://www.thorcam.com/downloads/FLI_SDK_Documentation.pdf>`__ library for `Finger Lakes Instrumentation <https://www.thorcam.com>`__ cameras. It is built on top of `basecam <https://sdss-basecam.readthedocs.io/en/latest/>`__.

To install ``thorcam`` do ::

  $ pip install sdss-thorcam

Then you can run the actor as ::

  $ thorcam start

More options and command, some of which allow to command the camera without executing the actor, can be consulted :ref:`here <cli>` or by running ``thorcam --help``.

``thorcam`` can also be :ref:`run as a Docker <docker>`.


Contents
--------

.. toctree::
  :maxdepth: 2

  Configuring a computer <nuc>
  docker
  api
  CLI <cli>
  changelog



Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
