import flask

import config
from groupie import indexer, models, VERSION

app = flask.Flask('groupie.web')
app.config.from_object(config)

@app.context_processor
def common_vars():
    return {'group': models.Group.get(), 'GROUPIE_VERSION': VERSION}

@app.template_filter()
def format_time(time):
    return time.strftime('%Y-%m-%d')

@app.template_filter()
def nl2br(text):
    return flask.Markup('<br>').join(text.splitlines())

@app.route('/')
def index():
    q = flask.request.args.get('q', '').strip()
    sort = flask.request.args.get('sort', 'popular').strip()
    result = error = None
    if q:
        if len(q) <= 1:
            error = 'Search query should be longer than 1 character.'
        else:
            result = indexer.search(q, sort)

    return flask.render_template('index.html', q=q, sort=sort, error=error, result=result)
