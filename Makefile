test:
	tox

.PHONY: build
build:
	rm -f dist/* && python3 -m pip install --upgrade poetry && poetry build && ./rename-wheel.sh

frontend_build:
	yarn webui:install && yarn webui:build

release: build
	twine upload dist/*

build_docs:
	sphinx-build -b html docs/ docs/_build/

changelog:
	@echo "Not supported any more. Run ./generate_changelog.py <version_number> instead!"
