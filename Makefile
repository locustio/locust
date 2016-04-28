test:
	unit2 discover

release:
	python setup.py sdist upload

build_docs:
	sphinx-build -b html docs/ docs/_build/
