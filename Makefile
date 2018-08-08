install:
	pip install -e client/
	pip install server/

run:
	cd server
	python -m swagger_server
