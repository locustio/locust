coverage:
	coverage run -m unittest discover

test:
	tox

build:
	rm -f dist/* && python setup.py sdist bdist_wheel

release: build
	twine upload dist/*

build_docs:
	sphinx-build -b html docs/ docs/_build/
