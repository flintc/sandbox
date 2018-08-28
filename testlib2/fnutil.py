
import builtins
import re 
import functools as ft 

def arg_type_error(e):
    if re.match('[\w\W]*missing*(\d)*',str(e)):
        return True
    elif re.match('[\w\W]*expected*[\w\W]*arg*',str(e)):
        return True
    return False


def curry(fn):
    wfn = fn.func if hasattr(fn,'func') else fn
    @ft.wraps(wfn)
    def wrapper(*arg,**kwargs):
        try:
            return fn(*arg,**kwargs)
        except Exception as e:
            if not arg_type_error(e):
                raise e
            if hasattr(fn,'func'):
                return curry(ft.partial(fn.func,*fn.args,*arg,**fn.keywords,**kwargs))
            else:
                return curry(ft.partial(fn,*arg,**kwargs))
    return wrapper

@curry
def map(fn,gn):
    return lambda x: fn(gn(x))

@curry
def contramap(fn,gn):
    return lambda x: gn(fn(x))

@curry
def promap(before,after,fn):
    return map(after,contramap(before,fn))


@curry
def memoizer(is_full,contains,popitem,update,lookup,fn,x):
    if not contains(x):
        if is_full(): popitem()
        update(x,fn(x))
    return lookup(x)


def generator(fn):
    @ft.wraps(fn)
    def wrapper(*args,**kwargs):
        generate = fn(*args,**kwargs)
        next(generate)
        return generate
    return wrapper