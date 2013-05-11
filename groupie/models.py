import os
import datetime
import json

import config
from groupie.utils import get_path

class Base(object):
    def __init__(self, data):
        self.data = data

    def __getattr__(self, key):
        try:
            return self.data[key]
        except KeyError:
            return super(Base, self).__getattr__(key)

    @property
    def model(self):
        return self.__class__.__name__

class GroupNotFound(Exception):
    def __init__(self, slug):
        super(GroupNotFound, self).__init__("Group not found: %s" % slug)
        self.slug = slug

class Group(Base):
    @property
    def link(self):
        return 'https://www.facebook.com/groups/%s/' % self.id

    @staticmethod
    def get(slug):
        path = get_path(slug, 'info')
        if not os.path.exists(path):
            raise GroupNotFound(name)

        with open(get_path(slug, 'info')) as fp:
            group = Group(json.load(fp))
            group.slug = slug
            return group
    
    def get_path(self, *c):
        return get_path(self.slug, *c)

class Post(Base):
    @property
    def comments(self):
        for data in self.data.get('comments', {}).get('data', []):
            comment = Comment(data)
            comment.post = self
            yield comment
    
    @property
    def time(self):
        return datetime.datetime.strptime(self.created_time, '%Y-%m-%dT%H:%M:%S+0000')

    @property
    def like_count(self):
        return self.data.get('likes', {}).get('count', 0)

    @property
    def comment_count(self):
        return self.data.get('comments', {}).get('count', 0)
    
    @property
    def original_link(self):
        return 'https://www.facebook.com/groups/%s/posts/%s' % (self.group.id, self.id.split('_')[-1])

class Comment(Base):
    @property
    def link(self):
        '''Generate a permalink to the comment. UNDOCUMENTED'''
        return 'https://www.facebook.com/groups/%s/permalink/%s/?comment_id=%s' % (self.post.group.id, self.post.id.split('_')[-1], self.id.split('_')[-1])
