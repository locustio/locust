test:
	tox

.PHONY: build
build: setup_build
	rm -rf dist/* && poetry build && ./rename-wheel.sh

install: setup_build
	poetry install

.ONESHELL:
setup_build: check-yarn
	python3 -m pip install --upgrade poetry
	poetry self add "poetry-dynamic-versioning[plugin]"

.SILENT:
.PHONY: check-yarn
check-yarn:
	command -v yarn >/dev/null 2>&1 || { echo >&2 "Locust requires the yarn binary to be available in this shell to build the web front-end.\nSee: https://classic.yarnpkg.com/lang/en/docs/install"; exit 1; }

frontend_build:
	yarn webui:install && yarn webui:build

release: build
	twine upload dist/*

build_docs:
	sphinx-build -b html docs/ docs/_build/

changelog:
	@echo "Not supported any more. Run ./generate_changelog.py <version_number> instead!"
