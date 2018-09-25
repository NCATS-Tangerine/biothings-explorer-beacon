import connexion

from swagger_server import encoder
from flask import redirect

BASEPATH = '/beacon/biothings-explorer/'

def handle_error(e):
    return redirect(BASEPATH)

def main(name:str):
    """
    Usage in swagger_server/main.py:

        from beacon_controller import run
        if __name__ == '__main__':
            run(__name__)
    """
    app = connexion.App(name, specification_dir='./swagger/', server='tornado')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api(
        'swagger.yaml',
        base_path=BASEPATH,
        swagger_url='/',
        arguments={'title': 'Biothings Explorer Translator Knowledge Beacon API'}
    )
    app.add_error_handler(404, handle_error)
    app.run(port=8080)
