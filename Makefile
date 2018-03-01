init:
	pip install -r requirements.txt

test:
	py.test --cov leapp

.PHONY: init test
