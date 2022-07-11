MINIMUM_PYTHON_VERSION=3.5


all: pypi

.PHONY: test
test:
	python3 -m tests

.PHONY: mypy
mypy:
	mypy --python-version=$(MINIMUM_PYTHON_VERSION) --config-file mypy.conf typedload
	mypy --python-version=3.7 example.py

setup.py: docs/CHANGELOG.md README.md
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
	$(RM) -r html
	$(RM) -r perftest.output
	$(RM) docs/*_docgen.md

.PHONY: dist
dist: clean setup.py
	cd ..; tar -czvvf typedload.tar.gz \
		typedload/setup.py \
		typedload/Makefile \
		typedload/tests \
		typedload/docs \
		typedload/mkdocs.yml \
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
	mv /tmp/typedload_* /tmp/python3-typedload*.deb deb-pkg
	$(RM) -r /tmp/typedload
	lintian --pedantic -E --color auto -i -I deb-pkg/*.changes deb-pkg/*.deb

docs/typedload_docgen.md: typedload/__init__.py
	./docgen $@

docs/typedload.dataloader_docgen.md: typedload/dataloader.py
	./docgen $@

docs/typedload.datadumper_docgen.md: typedload/datadumper.py
	./docgen $@

docs/typedload.exceptions_docgen.md: typedload/exceptions.py
	./docgen $@

docs/typedload.typechecks_docgen.md: typedload/typechecks.py
	./docgen $@

html: \
		docs/typedload_docgen.md \
		docs/typedload.dataloader_docgen.md \
		docs/typedload.datadumper_docgen.md \
		docs/typedload.exceptions_docgen.md \
		docs/typedload.typechecks_docgen.md \
		mkdocs.yml \
		docs/CHANGELOG.md \
		docs/comparisons.md \
		docs/errors.md \
		docs/CONTRIBUTING.md \
		docs/gpl3logo.png \
		docs/CODE_OF_CONDUCT.md \
		docs/examples.md \
		docs/README.md \
		docs/supported_types.md \
		docs/SECURITY.md \
		docs/origin_story.md
	mkdocs build

.PHONY: publish_html
publish_html: html
	mkdocs gh-deploy

perftest.output/perf.p:
	perftest/performance.py

.PHONY: gnuplot
gnuplot: perftest.output/perf.p
	cd "perftest.output"; gnuplot -persist -c perf.p
