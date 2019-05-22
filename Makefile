vendor:
	pipenv lock -r > requirements.txt
	pip install -r requirements.txt --no-deps -t output
