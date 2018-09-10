
from typing import Mapping
from functools import reduce
from .core import zip_with,unwrap,fold,lift,spreadd,compose,wrap
import itertools as it
from copy import deepcopy

def keyed(value,key):
    return {key: value}

def merge(d1,d2):
    return dict(tuple(d1.items())+tuple(d2.items()))

def zip_merge(d1,d2):
    return [ merge(di,dj) for di,dj in zip(d1,d2) ]

def concat(a,b):
    return a+b

def deep_merger(list_combiner):
    def merge_deep(*d):
        def wrapper(d1_,d2_):
            d2 = deepcopy(d2_)
            d1 = deepcopy(d1_)
            for k,v in d1.items():
                if isinstance(v,dict) and k in d2.keys():
                    d2[k] = merge_deep(v,d2[k])
                elif (isinstance(v,list) or isinstance(v,tuple)) and k in d2.keys():
                    d2[k] = list_combiner(v, d2[k] )
            return merge(d1,d2)
        return reduce(lambda acc,x: wrapper(acc,x), d, dict())
    return merge_deep

merge_deep = deep_merger(zip_merge)
merge_deep_concat = deep_merger(concat)

def omit(x,*keys):
    return dict(tuple((k,v) for k,v in x.items() if k not in keys))

def pick(x,*keys):
    return omit(x,*(x.keys()-keys))

def pluck(x,*keys):
    return tuple(pick(x,*keys).values())

def prop(x,name):
    return x[name] if isinstance(x,Mapping) else getattr(x,name)

def kset(_x,**kwargs):
    x = deepcopy(_x)
    for k,v in kwargs.items():
        x[k] = v
    return x

def aset(x,**kwargs):
    for k,v in kwargs.items():
        setattr(x,k,v)
    return x

def assign(x,**kwargs):
    return kset(**kwargs)(x) if isinstance(x,Mapping) \
        else aset(**kwargs)(x)

def assign_multiple(value,*keys):
    return merge_deep(*list(zip_with(keyed,
        list(it.repeat(value,len(keys))),
        keys
    )))


def call(fn,keys):
    return lift( fold( dict, spreadd(assign) ), *map( fold(prop, compose(fn)),keys)  )
