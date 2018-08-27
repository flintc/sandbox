
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

