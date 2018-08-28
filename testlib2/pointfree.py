
from .core import curry

@curry
def map(fn,x):
    return x.map(fn)


@curry
def assign(key,value,x):
    return x.assign(key,value)

@curry
def get(value,x):
    return x.get(value)

def inspect(x):
    return x.inspect()

@curry
def set(key,value,x):
    return x.set(key,value)

@curry 
def over(key,fn,x):
    x.set(key,fn(x.get(key)))

def write(x):
    return x.write()


@curry
def filter(fn,x):
    return x.filter(fn)

@curry
def chain(fn,x):
    return x.chain(fn)


@curry
def extend(fn,x):
    return x.extend(fn)

@curry
def of(value,cls):
    return cls.of(value)

@curry
def append(y,x):
    return x.concat(x.of(y))

@curry 
def concat(y,x):
    return x.concat(y)

@curry
def contains(value,x):
    return x.contains(value)

@curry
def popitem(x):
    '''
    IMPURE
    '''
    x.popitem()
    return x