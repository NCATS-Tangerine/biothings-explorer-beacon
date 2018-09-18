install:
	pip install --no-cache-dir -r requirements.txt
	pip install client/
	pip install server/

dev-install:
	pip install --no-cache-dir -r requirements.txt
	pip install -e client/
	pip install server/

run:
	cd server
	python -m swagger_server

docker-build:
	docker build -t ncats:biothings-explorer-beacon .

docker-run:
	docker run --rm --name biothings -p 8084:8080 ncats:biothings-explorer-beacon

docker-stop:
	docker stop biothings

docker-logs:
	docker logs biothings
