SPECIFICATION=1.3.0.yaml

install:
	pip install .
	pip install beacon/

venv:
	virtualenv -p python3.6 venv

dev-install:
	pip install -e .
	pip install beacon/

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

regenerate:
	wget --no-clobber http://central.maven.org/maven2/io/swagger/swagger-codegen-cli/2.3.1/swagger-codegen-cli-2.3.1.jar -O swagger-codegen-cli.jar | true
	java -jar swagger-codegen-cli.jar generate -i ${SPECIFICATION} -l python-flask -o beacon
