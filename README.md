# Biothings Explorer Beacon

Knowledge beacon wrapper for http://biothings.io/explorer/api/

Hosted at https://kba.ncats.io/beacon/biothings-explorer

## Getting started

### Create virtual environment

It is helpful to keep a local virtual environment in which all local dependencies as well as the application can be installed.

```sh
virtualenv -p python3.6 venv
source venv/bin/activate
```

### Configuring

The [config/config.yaml](config/config.yaml) file can be modified to change some behaviours of this application.

### Installing the application

The [Makefile](Makefile) in the root directory can be used to install the application.

```shell
make install
```

### Running

The [Makefile](Makefile) in the root directory can be used to run the application:

```shell
make run
```

View it at http://localhost:8080

Alternatively you can run the application as a Docker container:

```shell
make docker-build
make docker-run
```

View it at http://localhost:8084

## Project structure


The `beacon` package was generated with Swagger, and the `beacon_controller` package is where all the implementation details are kept.

The `beacon` package can be regenerated with the Make command. But first make sure to update the `SPECIFICATION` parameter in [Makefile](Makefile) first if the specification file has a new name.

```
make regenerate
```

Alternatively, you can run swagger-codegen-cli.jar directly:

```
java -jar swagger-codegen-cli.jar generate -i <path-to-specification-file> -l python-flask -o beacon
```

Do a careful `git diff` review of the project after regenerating to make sure that nothing vital was overwritten, and to see all the changes made. Since we keep all implementation details in `beacon_controller` there shouldn't be much to worry about, and the only thing you will need to do is plug the `beacon_controller` package back in. Again, a `git diff` will show where this needs to be done.
