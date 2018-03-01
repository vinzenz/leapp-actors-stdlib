install:
	pip install -r requirements.txt

test:
	py.test --cov leapp

.PHONY: install test
