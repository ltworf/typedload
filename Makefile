all: pypi

.PHONY: test
test:
	python3 -m tests

.PHONY: mypy
mypy:
	mypy --config-file mypy.conf typedload

pypi: setup.py typedload
	mkdir -p dist pypi
	./setup.py sdist
	mv dist/typedload-`./setup.py --version`.tar.gz pypi
	rmdir dist
	gpg --detach-sign -a pypi/typedload-`./setup.py --version`.tar.gz

clean:
	$(RM) -r pypi
	$(RM) -r docs
	$(RM) -r .mypy_cache
	$(RM) MANIFEST
	$(RM) -r `find . -name __pycache__`
	$(RM) typedload_`./setup.py --version`.orig.tar.gz
	$(RM) typedload_`./setup.py --version`.orig.tar.gz.asc
	$(RM) -r deb-pkg

.PHONY: dist
dist: clean
	cd ..; tar -czvvf typedload.tar.gz \
		typedload/setup.py \
		typedload/Makefile \
		typedload/tests \
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
	cd /tmp/typedload/; dpkg-buildpackage
	mkdir deb-pkg
	mv /tmp/typedload_* /tmp/python3-typedload_*.deb deb-pkg
	$(RM) -r /tmp/typedload

docs:
	install -d docs
	pydoc3 -w typedload
	pydoc3 -w typedload.datadumper
	pydoc3 -w typedload.dataloader
	pydoc3 -w typedload.exceptions
	pydoc3 -w typedload.typechecks
	pydoc3 -w typedload.plugins
	pydoc3 -w typedload.plugins.attrload
	pydoc3 -w typedload.plugins.attrdump
	mv *.html docs
	ln -s typedload.html docs/index.html
