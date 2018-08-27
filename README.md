# biothings-explorer-beacon
Instructions to run in a virtual environment:
```
virtualenv -p python3.5 venv
source venv/bin/activate
make
make run
```
View it at: http://localhost:8080

Instructions to run in docker (mapping the hosts port 8097 to the containers port 8080):
```
make docker-build
make docker-run
```
View it at: http://localhost:8084
