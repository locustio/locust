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

push_%:
	docker build -f Dockerfile . -t t2gp/locust
	aws ecr get-login-password --region us-east-1 --profile $* | docker login --username AWS --password-stdin 354767525209.dkr.ecr.us-east-1.amazonaws.com
	docker tag locustio/locust:latest 354767525209.dkr.ecr.us-east-1.amazonaws.com/locustio/locust:latest
	docker push 354767525209.dkr.ecr.us-east-1.amazonaws.com/locustio/locust:latest
