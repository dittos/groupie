class Base(object):
    def __init__(self, data):
        self.data = data

    def __getattr__(self, key):
        try:
            return self.data[key]
        except KeyError:
            raise AttributeError

    @property
    def model(self):
        return self.__class__.__name__

class Post(Base):
    @property
    def comments(self):
        return map(Comment, self.data.get('comments', {}).get('data', []))

class Comment(Base):
    pass
