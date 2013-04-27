import os
import json

from groupie import models
from groupie.utils import get_path

def get_ids(dir):
    if not os.path.exists(dir): return []

    def sort_key(filename):
        return map(int, filename.split('_'))

    files = []
    for filename in os.listdir(dir):
        if filename.startswith('.'): continue
        files.append(filename)
    files.sort(key=sort_key)
    return files

def get_post_ids():
    return get_ids(get_path('posts'))

def get_posts_by_ids(ids):
    for post_id in ids:
        with open(get_path('posts', post_id)) as fp:
            yield models.Post(json.load(fp))

def get_post_comments(post):
    for comment_id in get_ids(get_path('comments', post.id)):
        with open(get_path('comments', post.id, comment_id)) as fp:
            comment = models.Comment(json.load(fp))
            comment.post = post
            yield comment

BODY_KEYS = ('message', 'name', 'caption', 'description')

COMMENT_POP_WEIGHT = 2
def popularity_func(obj):
    if isinstance(obj, models.Comment):
        obj = obj.post

    return obj.like_count + obj.comment_count * COMMENT_POP_WEIGHT

def search(q, sort):
    g = search_gen(q, sort)
    if sort == 'popular':
        g = sorted(g, key=popularity_func, reverse=True)
    return g

def search_gen(q, sort):
    q = q.lower()
    post_ids = get_post_ids()
    if sort == 'new':
        post_ids = reversed(post_ids)
    for post in get_posts_by_ids(post_ids):
        found = False
        for key in BODY_KEYS:
            value = post.data.get(key)
            if value:
                if q in value.lower():
                    yield post
                    found = True
                    break

        if not found:
            for comment in get_post_comments(post):
                if q in comment.message.lower():
                    yield comment
                    break

if __name__ == '__main__':
    posts_dir = get_path('posts')
    for post_id in get_ids(posts_dir):
        with open(get_path('posts', post_id)) as fp:
            post = json.load(fp)
            print 'posts/%s:' % post['id'],
            msg = post.get('message') or post.get('description')
            msg = u' '.join(msg.splitlines())
            print '%s --%s' % (msg, post['from']['name'])

            comment_dir = get_path('comments', post['id'])
            for comment_id in get_ids(comment_dir):
                with open(os.path.join(comment_dir, comment_id)) as cfp:
                    comment = json.load(cfp)
                    print 'comments/%s/%s:' % (post['id'], comment['id']),
                    print '%s --%s' % (comment['message'], comment['from']['name'])
