# $Header$


.PHONY: develop install text dist register upload wintext windist livinglogic


develop:
	python$(PYVERSION) setup.py develop


install:
	python$(PYVERSION) setup.py install


text:
	python$(PYVERSION) `which doc2txt.py` --title "History" NEWS.xml NEWS
	python$(PYVERSION) `which doc2txt.py` --title "Requirements and installation" INSTALL.xml INSTALL


dist: text
	rm -rf dist/*
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar
	python$(PYVERSION) setup.py sdist --formats=zip
	cd dist && scp.py -v -uftp -gftp *.tar.gz *.tar.bz2 *.zip root@isar.livinglogic.de:~ftp/pub/livinglogic/pycoco/


register:
	python$(PYVERSION) setup.py register


upload: text
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar upload
	python$(PYVERSION) setup.py sdist --formats=zip upload


livinglogic: text
	python$(PYVERSION) setup.py sdist --formats=bztar,gztar
	python$(PYVERSION) setup.py sdist --formats=zip
	scp dist/*.tar.gz dist/*.tar.bz2 dist/*.zip intranet@intranet.livinglogic.de:~/documentroot/intranet.livinglogic.de/python-downloads/


wintext:
	python$(PYVERSION) C:\\\\Programme\\\\Python24\\\\Scripts\\\\doc2txt.py --title "History" NEWS.xml NEWS
	python$(PYVERSION) C:\\\\Programme\\\\Python24\\\\Scripts\\\\doc2txt.py --title "Requirements and installation" INSTALL.xml INSTALL


windist: wintext
	python$(PYVERSION) setup.py bdist --formats=wininst
	python$(PYVERSION) setup.py bdist --formats=egg
	cd dist && python -mscp -v -uftp -gftp *.exe *.egg root@isar.livinglogic.de:~ftp/pub/livinglogic/pycoco/


winupload: wintext
	python$(PYVERSION) setup.py bdist --formats=wininst upload
	python$(PYVERSION) setup.py bdist --formats=egg upload


winlivinglogic: wintext
	python$(PYVERSION) setup.py bdist --formats=wininst
	python$(PYVERSION) setup.py bdist --formats=egg
	cd dist && python$(PYVERSION) -mscp -v -uintranet -gintranet *.exe *.egg intranet@intranet.livinglogic.de:~/documentroot/intranet.livinglogic.de/python-downloads/
