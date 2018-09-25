FROM python:3-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
COPY beacon_controller /usr/src/app/
COPY config /usr/src/app/
COPY server /usr/src/app/

COPY Makefile /usr/src/app/
COPY MANIFEST.in /usr/src/app/
COPY setup.py /usr/src/app/

RUN make && make run

EXPOSE 8080

ENTRYPOINT ["python3"]

CMD ["-m", "swagger_server"]
