# -*- coding: utf-8 -*-


from __future__ import with_statement

import sys, os, re, datetime, urllib, optparse, contextlib, subprocess, codecs

from ll import sisyphus, url, ul4c

from pycoco import xmlns


encodingdeclaration = re.compile(r"coding[:=]\s*([-\w.]+)")


class File(object):
	def __init__(self, name):
		self.name = name
		self.lines = [] # list of lines with tuples (# of executions, line)

	def __repr__(self):
		return "<File name=%r at 0x%x>" % (self.name, id(self))


class Python_GenerateCodeCoverage(sisyphus.Job):
	argdescription = "Generate code coverage info for the Python source code"
	projectname = "Python"
	jobname = "GenerateCodeCoverage"
	maxtime = 6* 60 * 60 # 6 hours

	def __init__(self):
		self.url = url.URL("http://svn.python.org/snapshots/python3k.tar.bz2")
		self.outputdir = url.Dir("~/pycoco")

		self.configurecmd = "./configure --enable-unicode=ucs4 --with-pydebug"

		self.gcovcmd = os.environ.get("COV", "gcov")
		self.makefile = "python/Makefile"

		self.buildlog = [] # the output of configuring and building Python
		self.testlog = [] # the output of running the test suite

	def cmd(self, cmd):
		self.log(">>> %s" % cmd)
		pipe = subprocess.Popen(cmd, shell=True, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout
		lines = []
		for line in pipe:
			self.log("... " + line)
			lines.append(line)
		return lines

	def files(self, base):
		with self.prefix("files: "):
			self.log("### finding files")
			allfiles = []
			for (root, dirs, files) in os.walk(base):
				for file in files:
					if file.endswith(".py") or file.endswith(".c"):
						allfiles.append(File(os.path.join(root, file)))
			self.log("### found %d files" % len(allfiles))
			return allfiles

	def download(self):
		with self.prefix("download: "):
			self.log("### downloading %s to %s" % (self.url, self.url.file))
			urllib.urlretrieve(str(self.url), str(self.url.file))

	def unpack(self):
		with self.prefix("unpack: "):
			self.log("### unpacking %s" % self.url.file)
			self.cmd("tar xvjf %s" % self.url.file)
			lines = list(open("python/.timestamp", "r"))
			self.timestamp = datetime.datetime.fromtimestamp(int(lines[0]))
			self.revision = lines[2]

	def configure(self):
		with self.prefix("configure: "):
			self.log("### configuring")
			lines = self.cmd("cd python; %s" % self.configurecmd)
			self.buildlog.extend(lines)

	def make(self):
		with self.prefix("make: "):
			self.log("### running make")
			self.buildlog.extend(self.cmd("cd python && make coverage"))

	def test(self):
		with self.prefix("test: "):
			self.log("### running test")
			lines = self.cmd("cd python && ./python.exe Lib/test/regrtest.py --coverage --nocoverdir test_urllib")
			# lines = self.cmd("cd python && ./python Lib/test/regrtest.py --coverage --nocoverdir -uurlfetch,largefile,network,decimal")
			self.testlog.extend(lines)

	def cleanup(self):
		with self.prefix("cleanup: "):
			self.log("### cleaning up files from previous run")
			self.cmd("rm -rf python")
			self.cmd("rm %s" % self.url.file)

	def coveruncovered(self, file):
		with self.prefix("cover: "):
			self.log("### faking coverage info for uncovered file %r" % file.name)
			with open(file.name, "r") as f:
				file.lines = [(None, line.rstrip("\n")) for line in f]

	def coverpy(self, file):
		with self.prefix("cover: "):
			coverfilename = os.path.splitext(file.name)[0] + ".cover"
			self.log("### fetching coverage info for Python file %r from %r" % (file.name, coverfilename))
			try:
				with open(coverfilename, "r") as f:
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
			except IOError, exc:
				self.log.exc(exc)
				self.coveruncovered(file)

	def coverc(self, file):
		with self.prefix("cover: "):
			self.log("### fetching coverage info for C file %r" % file.name)
			dirname = os.path.dirname(file.name).split("/", 1)[-1]
			basename = os.path.basename(file.name)
			self.cmd("cd python && %s %s -o %s" % (self.gcovcmd, basename, dirname))
			try:
				with open("python/%s.gcov" % basename, "r") as f:
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
			except IOError, exc:
				self.log.exc(exc)
				self.coveruncovered(file)

	def makehtml(self, files):
		with self.prefix("html: "):
			# Generate main page
			self.log("### generating index page")
			template = ul4c.compile(xmlns.page(xmlns.filelist(), onload="files_prepare()").conv().string())
			s = template.renders(
				filename=None,
				now=datetime.datetime.now(),
				timestamp=self.timestamp,
				revision=self.revision,
				crumbs=[
					dict(title="Core Development", href="http://www.python.org/dev/"),
					dict(title="Code coverage", href=None),
				],
				files=[
					dict(
						name=file.name.split("/", 1)[-1],
						lines=len(file.lines),
						coverablelines=sum(line[0]>=0 for line in file.lines),
						coveredlines=sum(line[0]>0 for line in file.lines),
					) for file in files
				],
			)
			u = self.outputdir/"index.html"
			with contextlib.closing(u.openwrite()) as f:
				f.write(s.encode("utf-8"))

			# Generate page for each source file
			template = ul4c.compile(xmlns.page(xmlns.filecontent()).conv().string())
			for (i, file) in enumerate(files):
				filename = file.name.split("/", 1)[-1]
				self.log("### generating HTML %d/%d for %s" % (i+1, len(files), filename))
				s = template.renders(
					filename=filename,
					crumbs=[
						dict(title="Core Development", href="http://www.python.org/dev/"),
						dict(title="Code coverage", href="/index.html"),
						dict(title=filename, href=None),
					],
					lines=(
						dict(count=count, content=content.decode("latin-1").expandtabs(8)) for (count, content) in file.lines
					),
				)
				u = self.outputdir/(filename + ".html")
				with contextlib.closing(u.openwrite()) as f:
					f.write(s.encode("utf-8"))

			# Copy CSS/JS/GIF files
			for filename in ("coverage.css", "coverage_sortfilelist.css", "coverage.js", "spc.gif"):
				self.log("### copying %s" % filename)
				try:
					import pkg_resources
				except ImportError:
					data = open(os.path.join(os.path.dirname(__file__), filename), "rb").read()
				else:
					data = pkg_resources.resource_string(__name__, filename)
				with contextlib.closing((self.outputdir/filename).openwrite()) as f:
					f.write(data)

			self.log("### creating buildlog.txt")
			with contextlib.closing((self.outputdir/"buildlog.txt").openwrite()) as f:
				f.write("".join(self.buildlog))

			self.log("### creating testlog.txt")
			with contextlib.closing((self.outputdir/"testlog.txt").openwrite()) as f:
				f.write("".join(self.testlog))

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
		return "done with project Python (%s; %d files)" % (self.timestamp.strftime("%Y-%m-%d %H:%M:%S"), len(files))

	def argparser(self):
		p = sisyphus.Job.argparser(self)
		p.add_argument("-u", "--url", dest="url", help="URL of the Python tarball", default=str(self.url), type=url.URL)
		p.add_argument("-d", "--outputdir", dest="outputdir", help="Directory where to put the HTML files", default=str(self.outputdir), type=url.Dir)
		return p

	def parseargs(self, args=None):
		args = sisyphus.Job.parseargs(self, args)
		self.url = args.url
		self.outputdir = args.outputdir
		return args

	def detectencoding(self, filename):
		with open(filename, "rb") as f:
			for (i, line) in enumerate(f):
				match = encodingdeclaration.search(line)
				if match is not None:
					return match.group(1)
					break
				if i >= 2:
					break
		return "utf-8"


def main(args=None):
	sisyphus.executewithargs(Python_GenerateCodeCoverage(), args)
	return 0


if __name__=="__main__":
	sys.exit(main())
