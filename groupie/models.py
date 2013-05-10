class Base(object):
    def __init__(self, data):
        self.data = data

    def __getattr__(self, key):
        return self.data[key]

    @property
    def model(self):
        return self.__class__.__name__

class Post(Base):
    @property
    def body(self):
        if self.type == 'status' or self.type == 'photo':
            return self.message
        elif self.type == 'link':
            return self.description
        elif self.type == 'video':
            return u'%s %s' % (self.name, self.link)
        return ''

    @property
    def comments(self):
        return map(Comment, self.data.get('comments', {}).get('data', []))

class Comment(Base):
    pass
