from functools import reduce,wraps,partial
from itertools import chain
import inspect 

_DEBUG = False

def caller(fn,*args,**kwargs):
    return fn(*args,**kwargs)

def spread(fn):
    @wraps(fn)
    def wrapper(args):
        return fn(*args)
    return wrapper

def spreadd(fn):
    @wraps(fn)
    def wrapper(args):
        return fn(**args)
    return wrapper

def gather(fn):
    @wraps(fn)
    def wrapper(*args):
        return fn(args)
    return wrapper

def compose(f):
    return lambda g: fold(g,f)

def tap(fn):
    def wrapper(x):
        fn(x)
        return x
    return wrapper

def logger(x):
    print(type(x),x.shape if hasattr(x,'shape') else x.keys() if isinstance(x,dict) else x) 

def fold(*fns):
    if _DEBUG:
        fns = [tap(logger)]+list(chain.from_iterable(zip(fns,[tap(logger)]*len(fns))))#+[tap(logger)]
    def wrapper(arg):
        return reduce( lambda x,fn: fn(x), fns, arg )
    return wrapper

def lift2(fn,x,y):
    return lambda data: fn(x(data),y(data))

def lift(fn,*xs):
    return lambda data: fn(*[x(data) for x in xs])

def evert(fn):
    @wraps(fn)
    def outer(*oargs,**okwargs):
        @wraps(fn)
        def inner(*iargs,**ikwargs):
            return fn(*iargs,**ikwargs)(*oargs,**okwargs)
        return inner
    return outer

def unwrap(fn):
    @wraps(fn)
    def wrapper(*args):
        return fn(args[0])(*args[1:])
    return wrapper

def wrap(fn):
    @wraps(fn)
    def outer(*oarg,**okwargs):
        @wraps(fn)
        def inner(*iarg,**ikwargs):
            return fn(*oarg,*iarg,**okwargs,**ikwargs)
        return inner
    return outer

def zip_with(fn,a,b):
    return map(spread(fn),zip(a,b))


def funzip(a,b):
    return zip_with(lambda fn,x: fn(x), a, b)

def unit(x):
    return [x]