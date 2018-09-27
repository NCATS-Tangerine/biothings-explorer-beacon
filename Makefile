install:
	pip install .
	pip install server/

dev-install:
	pip install -e .
	pip install server/

run:
	python -m swagger_server

docker-build:
	docker build -t ncats:biothings-explorer-beacon .

docker-run:
	docker run -d --rm --name biothings -p 8084:8080 ncats:biothings-explorer-beacon

docker-stop:
	docker stop biothings

docker-logs:
	docker logs biothings
