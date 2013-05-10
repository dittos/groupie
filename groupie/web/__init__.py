import flask

import config
from groupie import indexer

app = flask.Flask('groupie.web')
app.config.from_object(config)

@app.route('/')
def index():
    q = flask.request.args.get('q', '').strip()
    result = error = None
    if q:
        if len(q) <= 1:
            error = 'Search query should be longer than 1 character.'
        else:
            result = indexer.search(q)

    return flask.render_template('index.html', q=q, error=error, result=result)
