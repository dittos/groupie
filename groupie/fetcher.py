import os
import json
import urllib
import urlparse
import requests

import config
from groupie import models
from groupie.utils import get_path

def get_pointer(group):
    path = group.get_path('pointer')
    if os.path.exists(path):
        with open(path) as fp:
            return fp.read().strip()
    return None

def update_pointer(group, ptr):
    print 'Update pointer:', ptr
    if ptr is None:
        print 'Not updating...'
        return

    scheme, netloc, path, query, frag = urlparse.urlsplit(ptr)
    query = urlparse.parse_qs(query)
    for k, v in query.items():
        if k.startswith('__'):
            del query[k]
        else:
            query[k] = v[0] # XXX
    query = urllib.urlencode(query)
    ptr = urlparse.urlunsplit((scheme, netloc, path, query, frag))
    with open(group.get_path('pointer'), 'w') as fp:
        fp.write(ptr)

def fetch_comments(group, post):
    comments = post.get('comments')
    if not comments: return

    while True:
        for comment in comments.get('data', ()):
            comment_dir = ensure_dir(group.slug, 'comments', post['id'])
            with open(os.path.join(comment_dir, comment['id']), 'w') as fp:
                json.dump(comment, fp)

        next_url = comments.get('paging', {}).get('next')
        if not next_url:
            break
        print 'Fetching comments:', next_url
        comments = requests.get(next_url).json()

def update_posts(group, posts):
    for post in posts:
        fetch_comments(group, post)
        with open(group.get_path('posts', post['id']), 'w') as fp:
            json.dump(post, fp)

def fetch_feed(group, initial_url=None):
    only_once = True
    if not initial_url:
        only_once = False
        params = {'access_token': config.ACCESS_TOKEN, 'limit': str(100)}
        initial_url = 'https://graph.facebook.com/%s/feed?%s' % (urllib.quote(group.id), urllib.urlencode(params))

    update_url = None
    url = initial_url
    while url:
        print '*', url
        r = requests.get(url)
        data = r.json()
        update_posts(group, data.get('data', []))
        paging = data.get('paging', {})
        url = paging.get('next')
        if update_url is None:
            update_url = paging.get('previous')
        if only_once:
            break
    return update_url

def fetch_info(group):
    r = requests.get('https://graph.facebook.com/%s' % group.id)
    with open(group.get_path('info'), 'w') as fp:
        json.dump(r.json(), fp)

def ensure_dir(*c):
    path = get_path(*c)
    try:
        os.mkdir(path)
    except:
        if not os.path.exists(path):
            raise
    return path

def main(group_slug):
    print '** Fetching:', group_slug

    try:
        group = models.Group.get(group_slug)
    except models.GroupNotFound:
        group = models.Group({})
        group.slug = group_slug
        group.id = config.GROUPS[group_slug]

    ensure_dir(group.slug)
    ensure_dir(group.slug, 'posts')
    ensure_dir(group.slug, 'comments')
    fetch_info(group)
    update_pointer(group, fetch_feed(group, get_pointer(group)))
    print

if __name__ == '__main__':
    for slug in config.GROUPS:
        main(slug)
