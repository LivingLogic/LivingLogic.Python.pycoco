# -*- coding: iso-8859-1 -*-

import os, datetime, urllib

try:
	import pkg_resources
except ImportError:
	css = open(os.path.join(__file__, "coverage.css"), "rb").read()
else:
	css = pkg_resource.resource_string(__name__, "coverage.css")

from ll import sisyphus, url
from ll.xist import xsc
from ll.xist.ns import xml, html, meta, htmlspecials


class xmlns(xsc.Namespace):
	xmlname = "cov"
	xmlurl = "http://xmlns.python.org/coverage"

	class page(xsc.Element):
		class Attrs(xsc.Element.Attrs):
			class title(xsc.TextAttr): required = True
			class crumbs(xsc.TextAttr): required = True

		def convert(self, converter):
			e = xsc.Frag(
				xml.XML10(), "\n",
				html.DocTypeXHTML10transitional(), "\n",
				html.html(
					html.head(
						meta.contenttype(),
						html.title(self.attrs.title),
						html.link(type="text/css", rel="stylesheet", href="root:coverage.css"),
					),
					html.body(
						html.div(
							html.div(
								html.a(
									htmlspecials.autoimg(src="http://www.python.org/images/python-logo.gif", alt="Python", border=0),
									href="http://www.python.org/",
								),
								class_="logo",
							),
							html.div(
								self.attrs.crumbs,
								class_="crumbs",
							),
							class_="header",
						),
						html.div(
							self.content,
							class_="content",
						),
					),
				),
			)
			return e.convert(converter)


	class crumb(xsc.Element):
		class Attrs(xsc.Element.Attrs):
			class href(xsc.URLAttr): pass
			class first(xsc.BoolAttr): pass

		def convert(self, converter):
			if self.attrs.first:
				c = u"\xbb"
			else:
				c = ">"
			e = self.content
			if self.attrs.href:
				e = html.a(e, href=self.attrs.href)
			else:
				e = html.span(e, class_="here")
			e = html.span(html.span(c, class_="bullet"), e, class_="crumb")
			return e.convert(converter)


	class filelist(xsc.Element):
		class Attrs(xsc.Element.Attrs):
			class timestamp(xsc.TextAttr): pass
			class revision(xsc.TextAttr): pass
		def convert(self, converter):
			now = datetime.datetime.now()
			e = xsc.Frag(
				html.h1("Python code coverage"),
				html.p("Generated at ", now.strftime("%Y-%m-%d %H:%M:%S"), class_="note"),
				html.p(self.attrs.timestamp, class_="note"),
				html.p(self.attrs.revision, class_="note"),
				htmlspecials.plaintable(
					html.thead(
						html.tr(
							html.th("Filename"),
							html.th("# lines"),
							html.th("# coverable lines"),
							html.th("# covered lines"),
							html.th("coverage"),
							html.th("distribution"),
						),
					),
					html.tbody(
						self.content,
					),
					class_="files",
				)
			)
			return e.convert(converter)


	class fileitem(xsc.Element):
		class Attrs(xsc.Element.Attrs):
			class name(xsc.TextAttr): required = True
			class lines(xsc.IntAttr): required = True
			class coverablelines(xsc.IntAttr): required = True
			class coveredlines(xsc.IntAttr): required = True

		def convert(self, converter):
			lines = int(self.attrs.lines)
			coverablelines = int(self.attrs.coverablelines)
			coveredlines = int(self.attrs.coveredlines)

			distsize = (100, 8)
			if coverablelines:
				coverage = "%.02f%%" % (100.*coveredlines/coverablelines)
				coverageclass = "int"
				distribution = xsc.Frag()
				totalwidth = 0
				if coverablelines < lines:
					width = int(float(lines-coverablelines)/lines*distsize[0])
					distribution.append(htmlspecials.pixel(width=width, height=distsize[1], style="background-color: #ccc;"))
					totalwidth += width
				if coveredlines < coverablelines:
					width = int(float(coverablelines-coveredlines)/lines*distsize[0])
					distribution.append(htmlspecials.pixel(width=width, height=distsize[1], style="background-color: #f00;"))
					totalwidth += width
				if totalwidth < distsize[0]:
					width = distsize[0]-totalwidth
					distribution.append(htmlspecials.pixel(width=width, height=distsize[1], style="background-color: #0c0;"))
					totalwidth += width
			else:
				coverage = "n/a"
				coverageclass = "int disable"
				distribution = htmlspecials.pixel(width=distsize[0], height=distsize[1], style="background-color: #000;")

			e = html.tr(
				html.th(
					html.a(
						self.attrs.name,
						href=("root:", self.attrs.name, ".html"),
					),
					class_="filename",
				),
				html.td(
					lines,
					class_="int",
				),
				html.td(
					coverablelines,
					class_="int",
				),
				html.td(
					coveredlines,
					class_="int",
				),
				html.td(
					coverage,
					class_=coverageclass,
				),
				html.td(
					distribution,
					class_="dist",
				),
				class_="files",
			)
			return e.convert(converter)


	class filecontent(xsc.Element):
		class Attrs(xsc.Element.Attrs):
			class name(xsc.TextAttr): required = True

		def convert(self, converter):
			e = xsc.Frag(
				html.h1("Python code coverage for ", self.attrs.name),
				htmlspecials.plaintable(
					html.thead(
						html.tr(
							html.th("#"),
							html.th("count"),
							html.th("content"),
						),
					),
					html.tbody(
						self.content,
					),
					class_="file",
				)
			)
			return e.convert(converter)


	class fileline(xsc.Element):
		class Attrs(xsc.Element.Attrs):
			class lineno(xsc.IntAttr): required = True
			class count(xsc.IntAttr): required = True

		def convert(self, converter):
			class_ = None
			count = None
			if self.attrs.count:
				count = int(self.attrs.count)
				if not count:
					class_ = "uncovered"
				elif count == -1:
					class_ = "uncoverable"
					count = "n/a"
			else:
				class_ = "uncoverable"
				count = "n/a"
			e = html.tr(
				html.th(self.attrs.lineno),
				html.td(count, class_="count"),
				html.td(self.content, class_="line"),
				class_=class_
			)
			return e.convert(converter)


class File(object):
	def __init__(self, name):
		self.name = name
		self.lines = [] # list of lines with tuples (# of executions, line)

	def __repr__(self):
		return "<File name=%r at 0x%x>" % (self.name, id(self))


class Python_GenerateCodeCoverage(sisyphus.Job):
	def __init__(self):
		sisyphus.Job.__init__(self, 60*60, name="Python_GenerateCodeCoverage", raiseerrors=1)
		self.url = "http://svn.python.org/snapshots/python.tar.bz2"
		self.tarfile = "python.tar.bz2"
		self.outputdir = url.Dir("~/documentroot/coverage.livinglogic.de/")

		self.configurecmd = "./configure --enable-unicode=ucs4 --with-pydebug"
		self.compileopts = "-fprofile-arcs -ftest-coverage"
		self.linkopts = "-lgcov"
		self.gcovcmd = "gcov-3.4"
		self.makefile = "python/Makefile"

		self.buildlog = [] # the output of configuring and building Python
		self.testlog = [] # the output of running the test suite

	def cmd(self, cmd):
		self.logProgress(">>> %s" % cmd)
		pipe = os.popen(cmd + " 2>&1")
		lines = []
		for line in pipe:
			self.logProgress("... " + line)
			lines.append(line)
		return lines

	def files(self, base):
		self.logProgress("### finding files")
		allfiles = []
		for (root, dirs, files) in os.walk(base):
			for file in files:
				if file.endswith(".py") or file.endswith(".c"):
					allfiles.append(File(os.path.join(root, file)))
		self.logProgress("### found %d files" % len(allfiles))
		return allfiles

	def download(self):
		self.logProgress("### downloading %s to %s" % (self.url, self.tarfile))
		urllib.urlretrieve(self.url, self.tarfile)

	def unpack(self):
		self.logProgress("### unpacking %s" % self.tarfile)
		self.cmd("tar xvjf %s" % self.tarfile)
		lines = list(open("python/.timestamp", "r"))
		self.timestamp = datetime.datetime.fromtimestamp(int(lines[0]))
		self.revision = lines[2]

	def configure(self):
		self.logProgress("### configuring")
		lines = self.cmd("cd python; %s" % self.configurecmd)
		self.buildlog.extend(lines)
		makelines = []
		self.logProgress("### adding compiler options %s" % self.compileopts)
		for line in open(self.makefile, "r"):
			if line.startswith("OPT") and line[3:].strip().startswith("="):
				line = line.rstrip("\n") + " " + self.compileopts + "\n"
			if line.startswith("LIBC") and line[4:].strip().startswith("="):
				line = line.rstrip("\n") + " " + self.linkopts + "\n"
			makelines.append(line)
		file = open(self.makefile, "w")
		file.writelines(makelines)
		file.close()

	def make(self):
		self.logProgress("### running make")
		self.buildlog.extend(self.cmd("cd python && make"))

	def test(self):
		self.logProgress("### running test")
		lines = self.cmd("cd python && ./python Lib/test/regrtest.py -T -N -R :: -uurlfetch,largefile,network,decimal")
		self.testlog.extend(lines)

	def cleanup(self):
		self.logProgress("### cleaning up files from previous run")
		self.cmd("rm -rf python")
		self.cmd("rm %s" % self.tarfile)

	def coveruncovered(self, file):
		self.logProgress("### faking coverage info for uncovered file %r" % file.name)
		file.lines = [(None, line.rstrip("\n")) for line in open(file.name, "r")]

	def coverpy(self, file):
		coverfilename = os.path.splitext(file.name)[0] + ".cover"
		self.logProgress("### fetching coverage info for Python file %r from %r" % (file.name, coverfilename))
		try:
			f = open(coverfilename, "r")
		except IOError, exc:
			self.logError(exc)
			self.coveruncovered(file)
		else:
			for line in f:
				line = line.rstrip("\n")
				prefix, line = line[:7], line[7:]
				prefix = prefix.strip()
				if prefix == "." or prefix == "":
					file.lines.append((-1, line))
				elif prefix == ">"*len(prefix):
					file.lines.append((0, line))
				else:
					file.lines.append((int(prefix.rstrip(":")), line))
			f.close()

	def coverc(self, file):
		self.logProgress("### fetching coverage info for C file %r" % file.name)
		dirname = os.path.dirname(file.name).split("/", 1)[-1]
		basename = os.path.basename(file.name)
		self.cmd("cd python && %s %s -o %s" % (self.gcovcmd, basename, dirname))
		try:
			f = open("python/%s.gcov" % basename, "r")
		except IOError, exc:
			self.logError(exc)
			self.coveruncovered(file)
		else:
			for line in f:
				line = line.rstrip("\n")
				if line.count(":") < 2:
					continue
				(count, lineno, line) = line.split(":", 2)
				count = count.strip()
				lineno = lineno.strip()
				if lineno == "0": # just the header
					continue
				if count == "-": # not executable
					file.lines.append((-1, line))
				elif count == "#####": # not executed
					file.lines.append((0, line))
				else:
					file.lines.append((int(count), line))
			f.close()

	def makehtml(self, files):
		ns = xmlns
		# Generate page for each source file
		for (i, file) in enumerate(files):
			filename = file.name.split("/", 1)[-1]
			self.logProgress("### generating HTML %d/%d for %s" % (i+1, len(files), filename))
			e = ns.page(
				ns.filecontent(name=filename)(
					ns.fileline(
						content.decode("latin-1").expandtabs(8),
						lineno=i+1,
						count=count,
					)
					for (i, (count, content)) in enumerate(file.lines),
				),
				title=("Python code coverage: ", filename),
				crumbs=(
					ns.crumb("Core Development", href="http://www.python.org/dev/", first=True),
					ns.crumb("Code coverage", href="root:index.html"),
					ns.crumb(filename),
				),
			)
			e = e.conv()
			u = self.outputdir/(filename + ".html")
			e.write(u.openwrite(), base="root:%s.html" % filename, encoding="utf-8")

		# Generate main page
		self.logProgress("### generating index page")
		e = ns.page(
			ns.filelist(
				(
					ns.fileitem(
						name=file.name.split("/", 1)[-1],
						lines=len(file.lines),
						coverablelines=sum(line[0]>=0 for line in file.lines),
						coveredlines=sum(line[0]>0 for line in file.lines),
					)
					for file in files
				),
				timestamp=("Repository timestamp ", self.timestamp.strftime("%Y-%m-%d %H:%M:%S")),
				revision=self.revision,
			),
			title=("Python code coverage (", self.timestamp.strftime("%Y-%m-%d"), ")"),
			crumbs=(
				ns.crumb("Core Development", href="http://www.python.org/dev/", first=True),
				ns.crumb("Code coverage"),
			),
		)
		e = e.conv()
		u = self.outputdir/"index.html"
		e.write(u.openwrite(), base="root:index.html", encoding="utf-8")

		# Copy CSS file
		self.logProgress("### saving CSS file")
		(self.outputdir/"coverage.css").openwrite().write(css)

	def execute(self):
		self.cleanup()
		self.download()
		self.unpack()
		self.configure()
		files = self.files("python")
		self.make()
		self.test()
		for file in files:
			if file.name.endswith(".py"):
				self.coverpy(file)
			elif file.name.endswith(".c"):
				self.coverc(file)
		self.makehtml(files)
		self.logLoop("done with project Python (%s; %d files)" % (self.timestamp.strftime("%Y-%m-%d %H:%M:%S"), len(files)))

if __name__=="__main__":
	sisyphus.execute(Python_GenerateCodeCoverage())
