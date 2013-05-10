import os
import json

from groupie.utils import get_path

def get_ids(dir):
    def sort_key(filename):
        return map(int, filename.split('_'))

    files = []
    for filename in os.listdir(dir):
        if filename.startswith('.'): continue
        files.append(filename)
    files.sort(key=sort_key)
    return files

posts_dir = get_path('posts')
for post_id in get_ids(posts_dir):
    with open(get_path('posts', post_id)) as fp:
        post = json.load(fp)
        print 'posts/%s:' % post['id'],
        msg = post.get('message') or post.get('description')
        msg = u' '.join(msg.splitlines())
        print '%s --%s' % (msg, post['from']['name'])
        if 'comments' in post:
            comment_dir = get_path('comments', post['id'])
            for comment_id in get_ids(comment_dir):
                with open(os.path.join(comment_dir, comment_id)) as cfp:
                    comment = json.load(cfp)
                    print 'comments/%s/%s:' % (post['id'], comment['id']),
                    print '%s --%s' % (comment['message'], comment['from']['name'])
