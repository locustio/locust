coverage:
	coverage run -m unittest discover

test:
	tox

build:
	rm -f dist/* && python setup.py sdist

release: build
	twine upload dist/*

build_docs:
	sphinx-build -b html docs/ docs/_build/
