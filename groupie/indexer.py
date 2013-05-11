import os
import json
import itertools

from groupie import models

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

def get_post_ids(group):
    return get_ids(group.get_path('posts'))

def get_posts_by_ids(group, ids):
    for post_id in ids:
        with open(group.get_path('posts', post_id)) as fp:
            post = models.Post(json.load(fp))
            post.group = group
            yield post

def get_post_comments(group, post):
    for comment_id in get_ids(group.get_path('comments', post.id)):
        with open(group.get_path('comments', post.id, comment_id)) as fp:
            comment = models.Comment(json.load(fp))
            comment.post = post
            yield comment

BODY_KEYS = ('message', 'name', 'caption', 'description')

COMMENT_POP_WEIGHT = 2
def popularity_func(obj):
    if isinstance(obj, models.Comment):
        obj = obj.post

    return obj.like_count + obj.comment_count * COMMENT_POP_WEIGHT

def search(group, q, sort, page, limit):
    g = search_gen(group, q, sort)
    if sort == 'popular':
        g = sorted(g, key=popularity_func, reverse=True)
    start = (page - 1) * limit
    end = start + limit + 1
    result = list(itertools.islice(g, start, end))
    if len(result) > limit:
        result = result[:limit]
        next_page = page + 1
    else:
        next_page = None
    return result, next_page

def search_gen(group, q, sort):
    q = q.lower()
    post_ids = get_post_ids(group)
    if sort == 'new':
        post_ids = reversed(post_ids)
    for post in get_posts_by_ids(group, post_ids):
        found = False
        for key in BODY_KEYS:
            value = post.data.get(key)
            if value:
                if q in value.lower():
                    yield post
                    found = True
                    break

        if not found:
            for comment in get_post_comments(group, post):
                if q in comment.message.lower():
                    yield comment
                    break
