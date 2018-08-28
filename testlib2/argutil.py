from .fnutil import curry
import functools as ft 
from .core import compose,gte,gather,spread

def merg_args(x,y):
    return x+y

def merge_kwargs(x,y):
    return dict(merg_args(tuple(x.items()),tuple(y.items())))

@curry
def call_when(pred,fn,pargs=tuple(),pkwargs=dict()):
    def wrapper(*args,**kwargs):
        nargs = merg_args(pargs,args)
        nkwargs = merge_kwargs(pkwargs,kwargs)
        return fn(*nargs,**nkwargs) if pred(nargs,nkwargs) else \
            call_when(pred,fn,nargs,nkwargs)
    return wrapper

def nargs(args,kwargs):
    return len(args)

@curry
def minimum(n,fn):
    return call_when(gather(compose(gte(n),spread(nargs))),fn)

@curry
def flip2(binop,x,y):
    return binop(y,x)

@curry
def ignore(n,fn):
    @ft.wraps(fn)
    def wrapper(*args,**kwargs):
        return fn(*args[n:],**kwargs)
    return wrapper


@curry
def ignore2(n,fn,*args,**kwargs):
    print(args,kwargs)
    return minimum(n+1)(fn)(*args[n:],**kwargs)

@curry
def only(n,fn,*args,**kwargs):
    return ignore(n,fn)(*reversed(args),**kwargs)

