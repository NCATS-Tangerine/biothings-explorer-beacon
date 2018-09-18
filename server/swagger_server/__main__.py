#!/usr/bin/env python3

import connexion

from swagger_server import encoder
from flask import redirect

BASEPATH = '/beacon/biothings-explorer/'

def handle_error(e):
    return redirect(f'{BASEPATH}ui/')

def main():
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api(
        'swagger.yaml',
        base_path=BASEPATH,
        arguments={'title': 'Biothings Explorer Translator Knowledge Beacon API'}
    )
    app.add_error_handler(404, handle_error)
    app.run(port=8080)


if __name__ == '__main__':
    main()
