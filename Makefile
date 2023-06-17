MINIMUM_PYTHON_VERSION=3.8


all: pypi

.PHONY: test
test:
	python3 -m tests

.PHONY: mypy
mypy:
	mypy --python-version=$(MINIMUM_PYTHON_VERSION) --config-file mypy.conf typedload
	mypy --python-version=$(MINIMUM_PYTHON_VERSION) example.py

pyproject.toml: docs/CHANGELOG.md
	./gensetup.py --$@

setup.py: docs/CHANGELOG.md README.md
	./gensetup.py --$@
	chmod u+x setup.py

pypi: pyproject.toml setup.py typedload
	mkdir -p dist pypi
	./setup.py sdist
	./setup.py bdist_wheel
	mv dist/typedload-`head -1 CHANGELOG`.tar.gz pypi
	mv dist/*whl pypi
	rmdir dist
	gpg --detach-sign -a pypi/typedload-`head -1 CHANGELOG`.tar.gz
	gpg --detach-sign -a pypi/typedload-`head -1 CHANGELOG`-py3-none-any.whl

.PHONY: clean
clean:
	$(RM) -r pypi
	$(RM) -r .mypy_cache
	$(RM) -r typedload.egg-info/
	$(RM) MANIFEST
	$(RM) -r `find . -name __pycache__`
	$(RM) typedload_`head -1 CHANGELOG`.orig.tar.gz
	$(RM) typedload_`head -1 CHANGELOG`.orig.tar.gz.asc
	$(RM) -r deb-pkg
	$(RM) setup.py
	$(RM) pyproject.toml
	$(RM) -r html
	$(RM) -r perftest.output
	$(RM) docs/*_docgen.md

.PHONY: dist
dist: clean setup.py pyproject.toml
	cd ..; tar -czvvf typedload.tar.gz \
		typedload/setup.py \
		typedload/Makefile \
		typedload/tests \
		typedload/docs \
		typedload/docgen \
		typedload/mkdocs.yml \
		typedload/LICENSE \
		typedload/CONTRIBUTING.md \
		typedload/CHANGELOG \
		typedload/README.md \
		typedload/example.py \
		typedload/mypy.conf \
		typedload/pyproject.toml \
		typedload/typedload
	mv ../typedload.tar.gz typedload_`./setup.py --version`.orig.tar.gz
	gpg --detach-sign -a *.orig.tar.gz

.PHONY: upload
upload: pypi
	twine upload --username __token__ --password `cat .token` pypi/*

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
		docs/*.svg \
		docs/CHANGELOG.md \
		docs/CODE_OF_CONDUCT.md \
		docs/comparisons.md \
		docs/CONTRIBUTING.md \
		docs/deferred_evaluation.md \
		docs/docs \
		docs/docs/gpl3logo.png \
		docs/errors.md \
		docs/examples.md \
		docs/gpl3logo.png \
		docs/origin_story.md \
		docs/performance.md \
		docs/README.md \
		docs/SECURITY.md \
		docs/supported_types.md \
		docs/typedload.datadumper_docgen.md \
		docs/typedload.dataloader_docgen.md \
		docs/typedload_docgen.md \
		docs/typedload.exceptions_docgen.md \
		docs/typedload.typechecks_docgen.md \
		mkdocs.yml
	mkdocs build
	# Download cloudflare crap
	mkdir -p html/cdn
	cd html/cdn; wget --continue `cat ../*html | grep cloudflare | grep min.css | sort | uniq | cut -d\" -f4`
	cd html/cdn; wget --continue `cat ../*html | grep cloudflare | grep min.js | sort | uniq | cut -d\" -f2`
	# Fix html pages
	for page in html/*.html; do \
		sed -i 's,https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.5.0/styles/github.min.css,cdn/github.min.css,g' $${page}; \
		sed -i 's,https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.5.0/highlight.min.js,cdn/highlight.min.js,g' $${page}; \
		echo "<!-- Trackers stripped from mkdocs theme by me -_-' -->" >> $${page}; \
	done

.PHONY: publish_html
publish_html: html
	git checkout gh-pages
	rm -rf cdn css docs fonts img js search
	mv html/* .
	git add cdn css docs fonts img js search
	git add `git status  --porcelain | grep '^ M' | cut -d\  -f3`
	git commit -m "Deployed manually to workaround MkDocs"
	git push
	git checkout -

perftest.output/perf.p:
	@echo export MOREVERSIONS=1 to compare more versions
	perftest/performance.py

.PHONY: gnuplot
gnuplot: perftest.output/perf.p
	cd "perftest.output"; gnuplot -persist -c perf.p
