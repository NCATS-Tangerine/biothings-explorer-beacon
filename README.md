# biothings-explorer-beacon
Instructions to run in a virtual environment:
```
virtualenv -p python3.5 venv
source venv/bin/activate
make
make run
```
Instructions to run in docker (mapping the hosts port 8097 to the containers port 8080):
```
make docker-build
make ports=8097:8080 docker-run
```
