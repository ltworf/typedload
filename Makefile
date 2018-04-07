all: pypi

.PHONY: test
test:
	python3 -m tests

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

.PHONY: dist
dist: clean
	cd ..; tar -czvvf typedload.tar.gz \
		typedload/setup.py \
		typedload/Makefile \
		typedload/tests \
		typedload/LICENSE \
		typedload/README.md \
		typedload/example.py \
		typedload/typedload
	mv ../typedload.tar.gz typedload_`./setup.py --version`.orig.tar.gz
	gpg --detach-sign -a *.orig.tar.gz

.PHONY: upload
upload: pypi
	twine upload pypi/typedload-`./setup.py --version`.tar.gz
