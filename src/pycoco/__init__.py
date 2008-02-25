# -*- coding: utf-8 -*-

import sys, os, datetime, urllib, optparse

from ll import sisyphus, url

from pycoco import xmlns


class File(object):
	def __init__(self, name):
		self.name = name
		self.lines = [] # list of lines with tuples (# of executions, line)

	def __repr__(self):
		return "<File name=%r at 0x%x>" % (self.name, id(self))


class Python_GenerateCodeCoverage(sisyphus.Job):
	def __init__(self, outputdir):
		sisyphus.Job.__init__(self, 60*60, name="Python_GenerateCodeCoverage", raiseerrors=1)
		self.url = "http://svn.python.org/snapshots/python.tar.bz2"
		self.tarfile = "python.tar.bz2"
		self.outputdir = url.Dir(outputdir)

		self.configurecmd = "./configure --enable-unicode=ucs4 --with-pydebug"
		self.compileopts = "-fprofile-arcs -ftest-coverage"
		self.linkopts = "-lgcov"
		self.gcovcmd = os.environ.get("COV", "gcov")
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
		lines = self.cmd("cd python && ./python Lib/test/regrtest.py -T -N")
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
		# Generate main page
		self.logProgress("### generating index page")
		e = xmlns.page(
			xmlns.filelist(
				(
					xmlns.fileitem(
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
				xmlns.crumb("Core Development", href="http://www.python.org/dev/", first=True),
				xmlns.crumb("Code coverage"),
			),
			onload="files_prepare()",
		)
		e = e.conv()
		u = self.outputdir/"index.html"
		e.write(u.openwrite(), base="root:index.html", encoding="utf-8")

		# Generate page for each source file
		for (i, file) in enumerate(files):
			filename = file.name.split("/", 1)[-1]
			self.logProgress("### generating HTML %d/%d for %s" % (i+1, len(files), filename))
			e = xmlns.page(
				xmlns.filecontent(name=filename)(
					xmlns.fileline(
						content.decode("latin-1").expandtabs(8),
						lineno=i+1,
						count=count,
					)
					for (i, (count, content)) in enumerate(file.lines)
				),
				title=("Python code coverage: ", filename),
				crumbs=(
					xmlns.crumb("Core Development", href="http://www.python.org/dev/", first=True),
					xmlns.crumb("Code coverage", href="root:index.html"),
					xmlns.crumb(filename),
				),
			)
			e = e.conv()
			u = self.outputdir/(filename + ".html")
			e.write(u.openwrite(), base="root:%s.html" % filename, encoding="utf-8")

		# Copy CSS/JS files
		for filename in ("coverage.css", "coverage_sortfilelist.css", "coverage.js"):
			self.logProgress("### copying %s" % filename)
			try:
				import pkg_resources
			except ImportError:
				data = open(os.path.join(os.path.dirname(__file__), filename), "rb").read()
			else:
				data = pkg_resources.resource_string(__name__, filename)
			(self.outputdir/filename).openwrite().write(data)

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


def main(args=None):
	p = optparse.OptionParser(usage="usage: %prog [options]")
	p.add_option("-o", "--outputdir", dest="outputdir", help="Directory where to put the HTML files", default="~/pycoco")
	(options, args) = p.parse_args(args)
	if len(args) != 0:
		p.error("incorrect number of arguments")
		return 1
	sisyphus.execute(Python_GenerateCodeCoverage(options.outputdir))
	return 0


if __name__=="__main__":
	sys.exit(main())
