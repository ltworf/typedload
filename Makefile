all: pypi

.PHONY: test
test:
	# Only run tests on python 3.6 or greater
	test `python3 --version | cut -d. -f2` -gt 5 && python3 -m tests || echo "WARNING: Skipping tests, python version is too old"

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
