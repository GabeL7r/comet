setup:
	pip install autopep8

lint:
	autopep8 --in-place --aggressive --aggressive *.py

deploy:
	python setup.py sdist bdist_wheel
	twine check dist/*
	twine upload dist/*

comet:
	. venv/bin/activate
	comet
