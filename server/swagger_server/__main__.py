#!/usr/bin/env python3

import connexion

from swagger_server import encoder
from flask import redirect

app = connexion.App(__name__, specification_dir='./swagger/')

@app.route('/')
def to_UI():
    return redirect('/ui')

def main():
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Translator Knowledge Beacon API'})
    app.run(port=8080)


if __name__ == '__main__':
    main()
