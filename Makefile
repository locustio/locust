test:
	tox

build:
	rm -f dist/* && python3 -m pip install --upgrade build && python3 -m build .

frontend_build:
	yarn webui:install && yarn webui:build

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
