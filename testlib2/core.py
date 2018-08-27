
from typing import Mapping
import itertools as it 
import operator as op
import functools as ft 
import re 
from collections import namedtuple
import builtins
from dataclasses import dataclass
from .fnutil import curry
# def arg_type_error(e):
#     if re.match('[\w\W]*missing*(\d)*',str(e)):
#         return True
#     elif re.match('[\w\W]*expected*[\w\W]*arg*',str(e)):
#         return True
#     return False

# def curry(fn):
#     wfn = fn.func if hasattr(fn,'func') else fn
#     @ft.wraps(wfn)
#     def wrapper(*arg,**kwargs):
#         try:
#             return fn(*arg,**kwargs)
#         except Exception as e:
#             if not arg_type_error(e):
#                 raise e
#             if hasattr(fn,'func'):
#                 return curry(ft.partial(fn.func,*fn.args,*arg,**fn.keywords,**kwargs))
#             else:
#                 return curry(ft.partial(fn,*arg,**kwargs))
#     return wrapper

@curry 
def partial_right(fn,*args,**kwargs):
    @ft.wraps(fn)
    def wrapper(*margs,**mkwargs):
        return fn(*margs,*args,**mkwargs,**kwargs)
    return wrapper 

@curry
def add(x,y):
    return x+y

@curry
def unit(x):
    return (x,)

@curry
def funzip(fns,args):
    return tuple([ fn(arg) for fn,arg in zip(fns,args)])
@curry
def getitem(item,obj):
    return obj[item]
@curry
def eq(a,b):
    return a==b

@curry
def binary(fn,x,y):
    return fn(x,y)

@curry
def lift2(fn,f,g):
    def wrapper(x):
        return fn(f(x),g(x))
    return wrapper

@curry
def ternary(fn,x,y,z):
    return fn(x,y,z)

@curry
def zip(x,y):
    return type(x)(builtins.zip(x,y))

@curry
def prop(key,dikt):
    return dikt[key] if isinstance(dikt,Mapping) else getattr(dikt,key)

@curry
def take(n,xs):
    return xs[0:n]

def head(xs):
    return xs[0]

def tail(xs):
    return xs[-1]

def identity(x):
    return x

@curry
def chunk(n, iterable, padvalue=None):
    "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
    return it.zip_longest(*[iter(iterable)]*n, fillvalue=padvalue)

@curry
def chunk_list(n, iterable, padvalue=None):
    "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
    return list(builtins.map(list,it.zip_longest(*[iter(iterable)]*n, fillvalue=padvalue)))


@curry
def first(transformer,fn):
    def first_call(*args,**kwargs):
        def second_call(y):
            return fn(transformer(*args,**kwargs),y)
        return second_call
    return first_call

def pipe(*fns):
    def wrapper(*args,**kwargs):
        return ft.reduce(
            lambda acc,fn: fn(acc),fns[1:],fns[0](*args,**kwargs)
        )
    return wrapper
def reverse(fn):
    def wrapper(*x):
        return fn(*reversed(x))
    return wrapper
compose = reverse(pipe)
@curry
def call(fn,x):
    return fn(x)

@curry
def rest(n,iterable):
    return iterable[n:]

drop = rest 

@curry
def lt(n,value):
    return value<n

@curry
def lte(n,value):
    return value<=n

@curry
def gt(n,value):
    return value>n

@curry
def gte(n,value):
    return value>=n

def iteratee(value):
    ''' 
    allows for various short-hand notations
    '''
    return identity if value is None \
        else value if callable(value) \
        else ( lambda obj: prop(k,obj)==v for k,v in pairs(value) ) if isinstance(value,Mapping) \
        else gather(compose(prop(value),head)) if isinstance(value,str) \
        else None

@curry
def times(n,i):
    return [iteratee(i)]*n

@curry
def partition(pred, iterable):
    'Use a predicate to partition entries into false entries and true entries'
    # partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
    t1, t2 = it.tee(iterable)
    return it.filterfalse(pred, t1), builtins.filter(pred, t2)

def encase(fn):
    @ft.wraps(fn)
    def wrapper(*args,**kwargs):
        try:
            result = fn(*args,**kwargs)
            return encase(result) if callable(result) and result.__name__==fn.__name__ else result
        except Exception as e:
            return e
    return wrapper

def arrows():
    Either = namedtuple('Either','left right')
    Left = namedtuple('Left','value')
    Right = namedtuple('Right','value')
    either = Either(Left,Right)
    def arrow():
        pass
    T = tuple
    def empty():
        return tuple()
    def unit(x):
        return (x,)
    def duplicate(x):
        return unit(x)+unit(x)
    def swap(x):
        return T(reversed(x))
    @curry
    def first(fn,iterable,from_second=False):    
        if from_second:
            print('second!',iterable)
        else:
            print('first!',iterable)
        result = unit(fn(head(iterable))) + drop(1,iterable)
        print('result: ',result)
        return result
    @binary
    def second(fn,iterable):
        print('second iterable: ',iterable)
        return pipe(swap, first(fn,from_second=True), swap)(iterable)
        #return take(1,iterable) + unit(fn(tail(iterable)))

    # ***
    @ternary
    def merge(fn1,fn2,iterable):
        return pipe(first(fn1),second(fn2) )(iterable)
        #return ft.reduce(lambda acc,x: acc+unit(x[1](x[0])), zip(iterable,fns), empty())
    @binary
    def merge_bin(fns,iterable):
        return pipe(first(head(fns)),second(tail(fns)))(iterable)

    arrow.duplicate = duplicate
    arrow.swap = swap
    arrow.first = first 
    arrow.second = second 
    arrow.merge = merge_bin
    arrow.unit = unit
    # &&&
    @ternary
    def andop(fn1,fn2,x):
        return merge(fn1,fn2,duplicate(x))
    @binary
    def andop_bin(fns,x):
        return merge_bin(fns,duplicate(x))
    def mirror(x):
        return either.left(x.value) if isinstance(x,either.right) else either.right(x.value)
    @binary
    def left(fn,x):
        #print('left!',fn.__name__,x)
        return either.left(fn(x.value)) if isinstance(x,either.left) else x
    @binary
    def right(fn,x):
        #print('right!',fn.__name__,x)
        return pipe(mirror,left(fn),mirror)(x)
    @binary 
    def loop(fn,xs):
        return T( zip(*map(fn,zip(*xs)) ) )
    @binary 
    def choice(fns,e):
        return pipe( left(head(fns)),right(tail(fns)) ) (e) 
    arrow.either = either
    arrow.mirror = mirror
    arrow.left = left 
    arrow.right = right 
    arrow.choice = choice
    arrow.andop = andop_bin 
    return arrow

def arrows_dual():
    Either = namedtuple('Either','left right')
    Left = namedtuple('Left','value')
    Right = namedtuple('Right','value')
    either = Either(Left,Right)
    def arrow():
        pass
    T = tuple
    def empty():
        return tuple()
    def unit(x):
        return (x,)
    def duplicate(x):
        return unit(x)+unit(x)
    def swap(x):
        return T(reversed(x))
    @curry
    def first(fn,iterable,from_second=False):    
        if from_second:
            print('second!',iterable)
        else:
            print('first!',iterable)
        result = unit( head(iterable)(fn) ) + drop(1,iterable)
        print('result: ',result)
        return result
    @binary
    def second(fn,iterable):
        print('second iterable: ',iterable)
        return pipe(swap, first(fn,from_second=True), swap)(iterable)
        #return take(1,iterable) + unit(fn(tail(iterable)))

    # ***
    @ternary
    def merge(fn1,fn2,iterable):
        return pipe(first(fn1),second(fn2) )(iterable)
        #return ft.reduce(lambda acc,x: acc+unit(x[1](x[0])), zip(iterable,fns), empty())
    @binary
    def merge_bin(fns,iterable):
        return pipe(first(head(fns)),second(tail(fns)))(iterable)

    arrow.duplicate = duplicate
    arrow.swap = swap
    arrow.first = first 
    arrow.second = second 
    arrow.merge = merge_bin
    # &&&
    @ternary
    def andop(fn1,fn2,x):
        return merge(fn1,fn2,duplicate(x))
    @binary
    def andop_bin(fns,x):
        return merge_bin(fns,duplicate(x))
    def mirror(x):
        return either.left(x.value) if isinstance(x,either.right) else either.right(x.value)
    @binary
    def left(fn,x):
        #print('left!',fn.__name__,x)
        return either.left(fn(x.value)) if isinstance(x,either.left) else x
    @binary
    def right(fn,x):
        #print('right!',fn.__name__,x)
        return pipe(mirror,left(fn),mirror)(x)
    @binary 
    def loop(fn,xs):
        return T( zip(*map(fn,zip(*xs)) ) )
    @binary 
    def choice(fns,e):
        return pipe( left(head(fns)),right(tail(fns)) ) (e) 
    arrow.either = either
    arrow.mirror = mirror
    arrow.left = left 
    arrow.right = right 
    arrow.choice = choice
    arrow.andop = andop_bin 
    return arrow



def gather(fn):
    @ft.wraps(fn)
    def wrapper(*xs):
        return fn(xs)
    return wrapper


def gatherd(fn):
    @ft.wraps(fn)
    def wrapper(**xs):
        return fn(xs)
    return wrapper

def spread(fn):
    @ft.wraps(fn)
    def wrapper(xs):
        return fn(*xs)
    return wrapper

def spreadd(fn):
    @ft.wraps(fn)
    def wrapper(xs):
        return fn(**xs)
    return wrapper

def pick(keys,dikt):
    return dict(ft.reduce(lambda acc,x: acc+prop(x,dikt),keys,tuple()))


def omit(keys,dikt):
    return pick(*(dikt.keys()-keys))(dikt)


def assign(destination,*sources):
    '''replaces duplicate keys and add non-duplicate keys in source(s) to destination'''
    return dict( 
        ft.reduce(lambda acc,x: acc+tuple(x.items()), sources, tuple(destination.items()) )
    )

def extend(destination,*sources):
    '''adds non-duplicate keys in source(s) to destination'''
    return dict( 
        ft.reduce(lambda acc,x: acc+tuple(x.items()), sources, tuple() ) + tuple(destination.items())
    )


def keys(obj):
    return tuple(obj.keys())

def values(obj):
    return tuple(obj.values())

@curry
def map(itee_value,obj):
    fn = iteratee(itee_value)
    return type(obj)(
        [ (k,fn(v,k)) for k,v in obj.items()]
    )

@curry
def ap(value,obj):
    #f = iteratee(itee_value)
    return type(obj)(
        [ (k, fn(value) ) for k,fn in obj.items()]
    )

def pairs(obj):
    return tuple(obj.items())


def invert(obj):
    return type(obj)( [(v,k) for k,v in obj.items()] )

@curry
def tap(interceptor,obj):
    interceptor(obj)
    return obj

@curry
def has(key,obj):
    return key in keys(obj)

@curry
def matches(attrs,obj):
    return [ prop(k,obj)==prop(k,attrs) for k in keys(attrs) ]


@dataclass 
class Lens:
    name: str = ''
    def set(self,obj,name,value):
        setattr(obj,name,value)
        return obj 
    def get(self,obj,name):
        print(self,obj,name)
        return getattr(obj,name)
    def __getattr__(self,name):
        return Lens(name)
@curry
def view(lens,obj):
    return lens.get(obj,lens.name)

@curry
def set(lens,value,obj):
    lens.set(obj,lens.name,value)
    return obj
@curry
def over(lens,fn,obj):
    lens.set(obj,lens.name,fn(view(lens,obj)))
    return obj