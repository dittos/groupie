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

class Group(Base):
    @property
    def link(self):
        return 'https://www.facebook.com/groups/%s/' % self.id

    @staticmethod
    def get():
        with open(get_path('info')) as fp:
            return Group(json.load(fp))

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
        return 'https://www.facebook.com/groups/%s/posts/%s' % (config.GROUP_ID, self.id.split('_')[-1])

class Comment(Base):
    @property
    def link(self):
        '''Generate a permalink to the comment. UNDOCUMENTED'''
        return 'https://www.facebook.com/groups/%s/permalink/%s/?comment_id=%s' % (config.GROUP_ID, self.post.id.split('_')[-1], self.id.split('_')[-1])
