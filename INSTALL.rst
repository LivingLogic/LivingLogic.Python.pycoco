Requirements
============

To use this module you need the following software packages:

	1.	`Python 2.5`_;
	2.	`ll-xist`_ (version 3.2 or later);

	.. _Python 2.5: http://www.python.org/
	.. _ll-xist: http://www.livinglogic.de/Python/Download.html#xist


Installation
============

distutils is used for installation, so it's rather simple. Execute the following
command::

	$ python setup.py install

For Windows a binary distribution is provided. To install it, double click it
and follow the instructions.

setuptools__ is supported for installation, so if you have setuptools installed
the package will be installed as an egg (and you can use ``easy_install`` for
installation).

__ http://peak.telecommunity.com/DevCenter/setuptools

If you have difficulties installing this software, send a problem report
to Walter Dörwald (walter@livinglogic.de).


Configuration
=============

In addition to the environment variables ``CC`` and ``CXX`` (which are used by
Python's Makefile itself for the C and C++ compiler), you can set the
environment variable ``COV`` to point to the coverage program (the default is
``gcov``).

You must create a directory ``run`` in your home directory, where :mod:`pycoco`
will put its pid file (log files will be put into ``~/log``, but this directory
will be created automatically).
