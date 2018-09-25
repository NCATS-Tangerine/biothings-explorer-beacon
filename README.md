# biothings-explorer-beacon

Hosted at https://kba.ncats.io/beacon/biothings-explorer

Instructions to run in a virtual environment:
```
virtualenv -p python3.6 venv
source venv/bin/activate
make
make run
```
View it at: http://localhost:8080

Instructions to run in docker:
```
make docker-build
make docker-run
```
View it at: http://localhost:8084

## Developer notes
The server sub-project has been generated with swagger and is only slightly modified. The `beacon_controller` package contains all the implementation code for the swagger generated server stub methods in `swagger_server/controllers/...`, and for the main method in `swagger_server/__main__.py`. The goal of this is to separate the implementation details from the generated code, and minimize what gets overwritten with each re-generation of the server sub-project.

> **Note:** with every re-generation of the server project, developers should do a git diff of each file to ensure that nothing important is being overwritten. It will be immediately obvious that the `swagger_server/controllers/...` files are overwritten as the beacon will stop functioning altogether. If the `swagger_server/__main__.py` file is overwritten the beacon will appear to function properly, but will lack important features!

Noteworthy changes to the generated main function:
- The Swagger UI path is set to the root
- The Swagger UI title is set in the code
- The base path is set in the code
- The [Tornado](https://connexion.readthedocs.io/en/1.0.29/quickstart.html#server-backend) server is used in the backend, as the default Flask server does not support concurrency
- 404 errors are redirected to the Swagger UI page
- The application is set to run on port 8080
