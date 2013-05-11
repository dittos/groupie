import os

try:
    import ujson as json
except ImportError:
    import json

import config

def get_path(*c):
    return os.path.join(config.DATA_DIR, *c)
