import flask

import config
from groupie import indexer, models, VERSION

app = flask.Flask('groupie.web')
app.config.from_object(config)

@app.context_processor
def common_vars():
    return {'GROUPIE_VERSION': VERSION}

@app.template_filter()
def format_time(time):
    return time.strftime('%Y-%m-%d')

@app.template_filter()
def nl2br(text):
    return flask.Markup('<br>').join(text.splitlines())

@app.route('/<group_slug>')
def index(group_slug):
    group = models.Group.get(group_slug)
    q = flask.request.args.get('q', '').strip()
    sort = flask.request.args.get('sort', 'popular').strip()
    page = flask.request.args.get('page', 1, int)
    limit = 20
    result = error = next_page = None
    if q:
        if len(q) <= 1:
            error = 'Search query should be longer than 1 character.'
        else:
            result, next_page = indexer.search(group, q, sort, page, limit)

    return flask.render_template('index.html', group=group, q=q, sort=sort, error=error, result=result, page=page, prev_page=page - 1, next_page=next_page, limit=limit)
