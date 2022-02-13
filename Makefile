coverage:
	coverage run -m unittest discover

test:
	tox

build:
	rm -f dist/* && python3 setup.py sdist bdist_wheel

release: build
	twine upload dist/*

build_docs:
	sphinx-build -b html docs/ docs/_build/

changelog:
	@echo "Not supported any more. Run ./generate_changelog.py <version_number> instead!"

sass_watch:
	sass --watch locust/static/sass:locust/static/css

sass_build:
	sass --update locust/static/sass:locust/static/css
