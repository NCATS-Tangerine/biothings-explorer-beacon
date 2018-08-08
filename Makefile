install:
	pip install --no-cache-dir -r requirements.txt
	pip install client/
	pip install server/

run:
	cd server
	python -m swagger_server

docker-build:
	docker build -t ncats:biothings-explorer-beacon .

docker-run:
	docker run --rm -p $(ports) ncats:biothings-explorer-beacon
