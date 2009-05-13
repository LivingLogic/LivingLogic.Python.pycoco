#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Setup script for pycoco


import re

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

try:
	news = list(open("NEWS.rst", "r"))
except IOError:
	description = DESCRIPTION.strip()
else:
	# Extract the first section (which are the changes for the current version)
	underlines = [i for (i, line) in enumerate(news) if line.startswith("---")]
	news = news[underlines[0]-1:underlines[1]-1]
	news = "".join(news)
	descr = "%s\n\n\n%s" % (DESCRIPTION.strip(), news)

	# Get rid of text roles PyPI doesn't know about
	descr = re.subn(":[a-z]+:`([a-zA-Z0-9_.]+)`", "``\\1``", descr)[0]

	# Expand tabs (so they won't show up as 8 spacces in the Windows installer)
	descr = descr.expandtabs(2)


args = dict(
	name="pycoco",
	version="0.6",
	description="Python code coverage",
	long_description=descr,
	author=u"Walter Doerwald",
	author_email="walter@livinglogic.de",
	url="http://www.livinglogic.de/Python/pycoco/",
	download_url="http://www.livinglogic.de/Python/Download.html#pycoco",
	license="Python",
	classifiers=sorted(set(c for c in CLASSIFIERS.strip().splitlines() if c.strip() and not c.strip().startswith("#"))),
	keywords=", ".join(sorted(set(k.strip() for k in KEYWORDS.strip().splitlines() if k.strip() and not k.strip().startswith("#")))),
	package_dir={"": "src"},
	packages=["pycoco"],
	package_data={
		"": ["*.css", "*.js", "*.gif"],
	},
	entry_points=dict(
		console_scripts=[
			"pycoco = pycoco:main",
		]
	),
	scripts=[
		"scripts/pycoco",
	],
	install_requires=[
		"ll-xist >= 3.6.4",
	],
	zip_safe=False,
)


if __name__ == "__main__":
	tools.setup(**args)
