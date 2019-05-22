.PHONY: all vendor test

vendor:
	pipenv lock -r > requirements.txt
	pipenv run pip install -r requirements.txt --no-deps -t output

test:
	echo 'test'
	pipenv run python -m pytest --cov=slackstorian --duration=5
