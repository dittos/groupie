import os

import config

def get_path(*c):
    return os.path.join(config.DATA_DIR, *c)
