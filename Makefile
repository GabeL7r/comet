setup:
	pip install autopep8

lint:
	autopep8 --in-place --aggressive --aggressive *.py

comet:
	. venv/bin/activate
	comet
