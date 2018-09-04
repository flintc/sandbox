import operator as op
from .core import wrap_publicmethods

def lift2(fn):
    return lambda x,y: lambda data: fn(x(data),y(data))


locals().update(wrap_publicmethods(lift2,op))