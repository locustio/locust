test:
	python setup.py test

release:
	python setup.py sdist upload

docs:
	sphinx-build -b html docs/ docs/_build/
