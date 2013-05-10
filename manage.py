from flask.ext.script import Manager
from groupie.web import app

manager = Manager(app)

if __name__ == '__main__':
    manager.run()
