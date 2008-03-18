# $Header$


.PHONY: develop install text dist register upload wintext windist livinglogic


develop:
	python$(PYVERSION) setup.py develop


install:
	python$(PYVERSION) setup.py install


dist:
	rm -rf dist/*
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar
	python$(PYVERSION) setup.py sdist --formats=zip
	python$(PYVERSION) -mll.scripts.ucp -v -uftp -gftp dist/*.tar.gz dist/*.tar.bz2 dist/*.zip ssh://root@isar.livinglogic.de/~ftp/pub/livinglogic/pycoco/


register:
	python$(PYVERSION) setup.py register


upload:
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar upload
	python$(PYVERSION) setup.py sdist --formats=zip upload


livinglogic:
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar
	python$(PYVERSION) setup.py sdist --formats=zip
	python$(PYVERSION) -mll.scripts.ucp -v dist/*.tar.gz dist/*.tar.bz2 dist/*.zip ssh://intranet@intranet.livinglogic.de/~/documentroot/intranet.livinglogic.de/python-downloads/


windist:
	python$(PYVERSION) setup.py bdist --formats=wininst
	python$(PYVERSION) setup.py bdist --formats=egg
	python -mll.scripts.ucp -v -cno -uftp -gftp dist/*.exe ssh://root@isar.livinglogic.de/~ftp/pub/livinglogic/pycoco/


winupload:
	python$(PYVERSION) setup.py bdist --formats=wininst upload
	python$(PYVERSION) setup.py bdist --formats=egg upload


winlivinglogic:
	python$(PYVERSION) setup.py bdist --formats=wininst
	python$(PYVERSION) setup.py bdist --formats=egg
	python$(PYVERSION) -mll.scripts.ucp -v -cno -uintranet -gintranet dist/*.exe ssh://intranet@intranet.livinglogic.de/~/documentroot/intranet.livinglogic.de/python-downloads/
