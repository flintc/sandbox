from itertools import filterfalse,tee
from functools import wraps
# class SeriesWrapper:
#     def __getattribute__(self,name):
#        return lambda series:  

import inspect

def partition(pred, iterable):
    'Use a predicate to partition entries into false entries and true entries'
    # partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
    t1, t2 = tee(iterable)
    return tuple(filterfalse(pred, t1)), tuple(filter(pred, t2))

def fncaller(fn):
    @wraps(fn)
    def wrapper(*args,**kwargs):
        return lambda obj: fn(obj,*args,**kwargs)
    return wrapper

def ispublicmethod(fn):
    return fn.startswith('_')

def wrap_publicmethods(wrapper,x):
    wrapped = dict()
    for fn_name in partition(ispublicmethod,dir(x))[0]:
        wrapped[fn_name] = wrapper( getattr(x,fn_name) )
    return wrapped