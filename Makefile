.PHONY: all setup test

setup:
	pipenv install --dev

test:
	pipenv run python -m pytest --cov=slackstorian --duration=5
