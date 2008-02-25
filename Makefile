# $Header$


.PHONY: develop install dist register upload windist livinglogic


develop:
	python$(PYVERSION) setup.py develop


install:
	python$(PYVERSION) setup.py install


dist:
	rm -rf dist/*
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar
	python$(PYVERSION) setup.py sdist --formats=zip
	cd dist && scp.py -v -uftp -gftp *.tar.gz *.tar.bz2 *.zip root@isar.livinglogic.de:~ftp/pub/livinglogic/pycoco/


register:
	python$(PYVERSION) setup.py register


upload:
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar upload
	python$(PYVERSION) setup.py sdist --formats=zip upload


livinglogic:
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar
	python$(PYVERSION) setup.py sdist --formats=zip
	scp dist/*.tar.gz dist/*.tar.bz2 dist/*.zip intranet@intranet.livinglogic.de:~/documentroot/intranet.livinglogic.de/python-downloads/


windist:
	python$(PYVERSION) setup.py bdist --formats=wininst
	python$(PYVERSION) setup.py bdist --formats=egg
	cd dist && python -mscp -v -uftp -gftp *.exe *.egg root@isar.livinglogic.de:~ftp/pub/livinglogic/pycoco/


winupload:
	python$(PYVERSION) setup.py bdist --formats=wininst upload
	python$(PYVERSION) setup.py bdist --formats=egg upload


winlivinglogic:
	python$(PYVERSION) setup.py bdist --formats=wininst
	python$(PYVERSION) setup.py bdist --formats=egg
	cd dist && python$(PYVERSION) -mscp -v -uintranet -gintranet *.exe *.egg intranet@intranet.livinglogic.de:~/documentroot/intranet.livinglogic.de/python-downloads/
