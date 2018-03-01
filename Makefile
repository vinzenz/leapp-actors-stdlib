install:
	pip install -r requirements-tests.txt

test:
	py.test --cov leapp

.PHONY: install test
