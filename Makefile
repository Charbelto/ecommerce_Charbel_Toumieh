.PHONY: build-debs clean

build-debs:
	python3 scripts/build_deb.py

clean:
	rm -rf build/
	find . -type d -name "deb_*" -exec rm -rf {} +