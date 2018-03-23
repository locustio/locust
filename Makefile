coverage:
	coverage run -m unittest discover

test:
	unit2 discover

release:
	rm dist/* && python setup.py sdist && twine upload dist/*

build_docs:
	sphinx-build -b html docs/ docs/_build/
