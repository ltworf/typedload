MINIMUM_PYTHON_VERSION=3.5


all: pypi

.PHONY: test
test:
	python3 -m tests

.PHONY: mypy
mypy:
	mypy --python-version=$(MINIMUM_PYTHON_VERSION) --config-file mypy.conf typedload
	mypy --python-version=3.7 example.py

setup.py:
	./gensetup.py > setup.py
	chmod u+x setup.py

pypi: setup.py typedload
	mkdir -p dist pypi
	./setup.py sdist
	mv dist/typedload-`head -1 CHANGELOG`.tar.gz pypi
	rmdir dist
	gpg --detach-sign -a pypi/typedload-`head -1 CHANGELOG`.tar.gz

.PHONY: clean
clean:
	$(RM) -r pypi
	$(RM) -r .mypy_cache
	$(RM) MANIFEST
	$(RM) -r `find . -name __pycache__`
	$(RM) typedload_`head -1 CHANGELOG`.orig.tar.gz
	$(RM) typedload_`head -1 CHANGELOG`.orig.tar.gz.asc
	$(RM) -r deb-pkg
	$(RM) setup.py

.PHONY: dist
dist: clean setup.py
	cd ..; tar -czvvf typedload.tar.gz \
		typedload/setup.py \
		typedload/Makefile \
		typedload/tests \
		typedload/docs \
		typedload/LICENSE \
		typedload/CONTRIBUTING.md \
		typedload/CHANGELOG \
		typedload/README.md \
		typedload/example.py \
		typedload/mypy.conf \
		typedload/typedload
	mv ../typedload.tar.gz typedload_`./setup.py --version`.orig.tar.gz
	gpg --detach-sign -a *.orig.tar.gz

.PHONY: upload
upload: pypi
	twine upload pypi/typedload-`./setup.py --version`.tar.gz

deb-pkg: dist
	mv typedload_`./setup.py --version`.orig.tar.gz* /tmp
	cd /tmp; tar -xf typedload_*.orig.tar.gz
	cp -r debian /tmp/typedload/
	cd /tmp/typedload/; dpkg-buildpackage --changes-option=-S
	mkdir deb-pkg
	mv /tmp/typedload_* /tmp/python3-typedload_*.deb deb-pkg
	$(RM) -r /tmp/typedload

site: mkdocs.yml README.md docs/examples.md docs/origin_story.md
	mkdocs build
	#install -d site/docstring
	#pydoc3 -w typedload
	#pydoc3 -w typedload.datadumper
	#pydoc3 -w typedload.dataloader
	#pydoc3 -w typedload.exceptions
	#pydoc3 -w typedload.typechecks
	#mv *.html site/docstring
	#ln -s typedload.html site/docstring/index.html
	mkdocs gh-deploy
