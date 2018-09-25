import connexion

from swagger_server import encoder
from flask import redirect

import config

def handle_error(e):
    return redirect(config.get('basepath'))

def main(name:str):
    """
    Usage in swagger_server/main.py:

        from beacon_controller import run
        if __name__ == '__main__':
            run(__name__)
    """
    app = connexion.App(name, specification_dir='./swagger/', server=config.get('server'))
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api(
        'swagger.yaml',
        base_path=config.get('basepath'),
        swagger_url='/',
        arguments={'title': config.get('title')}
    )
    app.add_error_handler(404, handle_error)
    app.run(port=8080)
