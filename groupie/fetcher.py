import os
import json
import urllib
import requests

import config
from groupie.utils import get_path

def get_pointer():
    path = get_path('pointer')
    if os.path.exists(path):
        with open(path) as fp:
            return fp.read().strip()
    return None

def update_pointer(ptr):
    print 'Update pointer:', ptr
    if ptr is None:
        print 'Not updating...'
        return
    with open(get_path('pointer'), 'w') as fp:
        fp.write(ptr)

def fetch_comments(post):
    comments = post.get('comments')
    if not comments: return

    while True:
        for comment in comments.get('data', ()):
            comment_dir = ensure_dir('comments', post['id'])
            with open(os.path.join(comment_dir, comment['id']), 'w') as fp:
                json.dump(comment, fp)

        next_url = comments.get('paging', {}).get('next')
        if not next_url:
            break
        print 'Fetching comments:', next_url
        comments = requests.get(next_url).json()

def update_posts(posts):
    for post in posts:
        fetch_comments(post)
        with open(get_path('posts', post['id']), 'w') as fp:
            json.dump(post, fp)

def fetch_feed(initial_url=None):
    if not initial_url:
        params = {'access_token': config.ACCESS_TOKEN, 'limit': str(100)}
        initial_url = 'https://graph.facebook.com/%s/feed?%s' % (urllib.quote(config.GROUP_ID), urllib.urlencode(params))

    update_url = None
    url = initial_url
    while url:
        print '*', url
        r = requests.get(url)
        data = r.json()
        update_posts(data.get('data', []))
        paging = data.get('paging', {})
        url = paging.get('next')
        if update_url is None:
            update_url = paging.get('previous')
    return update_url

def ensure_dir(*c):
    path = get_path(*c)
    try:
        os.mkdir(path)
    except:
        if not os.path.exists(path):
            raise
    return path

def main():
    ensure_dir()
    ensure_dir('posts')
    ensure_dir('comments')
    update_pointer(fetch_feed(get_pointer()))

if __name__ == '__main__':
    main()
