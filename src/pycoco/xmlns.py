# -*- coding: iso-8859-1 -*-

"""
This module is an &xist; namespace used for formatting the &html; coverage
report.
"""

import datetime

from ll.xist import xsc
from ll.xist.ns import xml, html, meta, htmlspecials


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


class __ns__(xsc.Namespace):
	xmlname = "cov"
	xmlurl = "http://xmlns.python.org/coverage"
__ns__.makemod(vars())