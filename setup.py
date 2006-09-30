#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Setup script for pycoco


__version__ = "$Revision$"[11:-2]
# $Source$


try:
	import setuptools as tools
except ImportError:
	from distutils import core as tools


DESCRIPTION = """pycoco is a script that can be used to generate code
coverage info for the Python source code.

The script downloads the Python source code, builds the interpreter
with code coverage options, runs the test suite and generates an HTML
report how often each source code line in each C or Python file has been
executed by the test suite.
"""


CLASSIFIERS="""
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: Python License (CNRI Python License)
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Testing
"""


KEYWORDS = """
Python
source code
subversion
test
code coverage
coverage
"""


args = dict(
	name="pycoco",
	version="0.1",
	description="Python code coverage",
	long_description=DESCRIPTION,
	author=u"Walter Doerwald",
	author_email="walter@livinglogic.de",
	url="http://www.livinglogic.de/Python/pycoco/",
	download_url="http://www.livinglogic.de/Python/pycoco/Download.html",
	license="Python",
	classifiers=[c for c in CLASSIFIERS.strip().splitlines() if c.strip() and not c.strip().startswith("#")],
	keywords=", ".join(k for k in KEYWORDS.strip().splitlines() if k.strip() and not k.strip().startswith("#")),
	package_dir={"": "src"},
	py_modules=["pycoco"],
	include_package_data=True, # includes the CSS file
)


if __name__ == "__main__":
	tools.setup(**args)
