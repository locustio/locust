test:
	tox

.PHONY: build
build: setup_dependencies
	rm -rf dist/* && poetry build && ./rename-wheel.sh

install: setup_dependencies
	poetry install

.ONESHELL:
setup_dependencies: check-poetry check-yarn
	poetry config virtualenvs.create false
	poetry self add "poetry-dynamic-versioning[plugin]"

.SILENT:
.PHONY: check-poetry
check-poetry:
	command -v poetry >/dev/null 2>&1 || { echo >&2 "Locust requires the poetry binary to be available in this shell to build the Python package.\nSee: https://docs.locust.io/en/stable/developing-locust.html#install-locust-for-development"; exit 1; }

.SILENT:
.PHONY: check-yarn
check-yarn:
	command -v yarn >/dev/null 2>&1 || { echo >&2 "Locust requires the yarn binary to be available in this shell to build the web front-end.\nSee: https://docs.locust.io/en/stable/developing-locust.html#making-changes-to-locust-s-web-ui"; exit 1; }

frontend_build:
	yarn webui:install && yarn webui:build

release: build
	twine upload dist/*

build_docs:
	sphinx-build -b html docs/ docs/_build/

changelog:
	@echo "Not supported any more. Run ./generate_changelog.py <version_number> instead!"
