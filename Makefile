setup:
	pip install autopep8

lint:
	autopep8 --in-place --aggressive --aggressive *.py

bundle:
	python setup.py sdist bdist_wheel

clean: 
	rm -rf dist

deploy: clean bundle
	twine check dist/*
	twine upload dist/*

comet:
	. venv/bin/activate
	comet
