from metamodel.utils.schemaloader import SchemaLoader

__schema = None

DEFAULT_EDGE_LABEL = 'related_to'
DEFAULT_CATEGORY = 'named thing'

def schema():
    global __schema

    if __schema is None:
        __schema = SchemaLoader('https://biolink.github.io/biolink-model/biolink-model.yaml').resolve()

    return __schema

def slot_uri(s:str) -> str:
    return f'https://biolink.github.io/biolink-model/docs/{s.replace(" ", "_")}.html'

def class_uri(c:str) -> str:
    camel_case = c.title().replace(' ', '')
    return f'https://biolink.github.io/biolink-model/docs/{camel_case}.html'
