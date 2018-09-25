import os, yaml

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')

with open(path, 'r') as f:
    config = yaml.load(f)

def get(*keys):
    d = config
    for key in keys:
        d = d[key]
    return d
