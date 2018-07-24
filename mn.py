import pandas as pd 
import numpy as np
import pymonad as md 
import pyramda as r 
from soup import at3
import bs4
def excepting(fn):
    def wrapper(*args,**kwargs):
        try:
            return fn(*args,**kwargs)
        except Exception as e:
            return e     
    return wrapper

class Base(object):
    level = -1
    @classmethod
    def inc_level(cls):
        Base.level += 1
    def __init__(self,value):
        self.value = value
        #self.value.__repr__ = lambda: str(value.__class__)
    def dec_level(cls):
        Base.level -= 1    
    def __str__(self):
        result = type(self).__name__ + '(' + self.value.__str__() + ')'
        return result
    def __repr__(self):
        self.inc_level()
        #result = "{}{}(\n{}\n{})\n".format(Base.level*'\t',type(self).__name__,type(self.value),Base.level*'\t')
        result = type(self).__name__ + self.value.__repr__()
        result = type(self).__name__ + '(' + self.value.__repr__() + ')'
        self.dec_level()
        #result = type(self).__name__ + '(\n' + self.value.__repr__() + '\n)'
        return result

maybe_none = r.if_else( r.equals(None), r.always(md.Nothing), md.Just )
maybe_empty = r.if_else( lambda x: len(x)==0, r.always(md.Nothing), md.Just )

@r.curry
def applymap(fn,x):
    return x.applymap(fn)


@r.curry
def apply(fn,x):
    return x.apply(fn)

def dropna(x):
    return x.dropna

class CallMaybeNone(object):
    def __getattribute__(self,name):
        def wrapper(*args,**kwargs):
            def invoker(x):
                result = getattr(x,name)(*args,**kwargs)
                return Just(result) if result is not None else Nothing
            return invoker
        return wrapper

class Invoker(object):
    def __init__(self,fn,ap):
        self._fn = fn 
        self.ap = ap
    def __call__(self,x):
        result = self._fn(x)
        return result
    def __getattr__(self,name):
        return getattr(self.ap, name)


class BaseApplier(object):
    def __init__(self,fn,resolver,decorator=lambda fn: fn):
        self._fn = fn 
        self.resolve = resolver
        self.decorator = decorator
    def __call__(self,*arg,**kwargs):
        pass


class Just(Base,BaseApplier,md.Just):
    def map( self, fn):
        return Just(fn(self.value))
    def chain( self, fn):
        return fn(self.value)
    def __add__(self,other):
        return self.value + other.value if isinstance(other,Just) else self
        
Nothing = md.Nothing
Nothing.chain = lambda self, fn: self.value
class MethodAp(BaseApplier):
    def __getattr__(self,name):
        #nfn = lambda *args,**kwargs: Invoker( lambda x: r.getattr(name)(self._fn(x))(*args,**kwargs), self )
        def wrapper(*args,**kwargs):
            def invoker(x):
                result = self.decorator( r.getattr( name, self._fn(x) ) )(*args,**kwargs)
                return self.resolve(result)
            return Invoker( invoker, MethodAp( invoker, self.resolve,self.decorator ) )
        return wrapper
        #return nfn
        #return r.getattr(name)
class ScalarAp(BaseApplier):
    def map(self,fn):
        def invoker(x):
            result = self.decorator(fn)( self._fn(x) ) 
            return self.resolve(result)
        return Invoker( invoker, ScalarAp( invoker, self.resolve,self.decorator )) 
        #return Invoker( r.map(self._fn), self.ap )
    def ap(self,fn):
        def invoker(x):
            result = self.decorator(fn)( self._fn(x) ) 
            return result
        return Invoker( invoker, ScalarAp( invoker, self.resolve,self.decorator )) 
        #return Invoker( r.map(self._fn), self.ap )
    def chain(self,fn):
        return self.ap(lambda x: fn(x.value))   

class IterableAp(BaseApplier):
    def map(self,fn):
        def invoker(x):
            result = r.map( self.decorator(fn), self._fn(x) ) 
            return r.map(self.resolve, result)
        return Invoker( invoker, IterableAp( invoker, self.resolve,self.decorator )) 
        #return Invoker( r.map(self._fn), self.ap )
    def ap(self,fn):
        def invoker(x):
            result = r.map( self.decorator(fn), self._fn(x) ) 
            return result
        return Invoker( invoker, IterableAp( invoker, self.resolve,self.decorator )) 
        #return Invoker( r.map(self._fn), self.ap )
    def chain(self,fn):
        return self.ap(lambda x: fn(x.value))

class CallMaybeEmpty(object):
    def __getattribute__(self,name):
        def wrapper(*args,**kwargs):
            def invoker(x):
                result = getattr(x,name)(*args,**kwargs)
                return Just(result) if len(result)!=0 else Nothing
            return invoker
        return wrapper

class IndexMaybeEmpty(object):
    def __getattribute__(self,name):
        class Tmp(object):
            def __getitem__(self,item):
                def wrapper(x):
                    result = getattr(x,name)[item]
                    return Just(result) if len(result)!=0 else Nothing
                return wrapper
        return Tmp()

mn = CallMaybeNone()
me = CallMaybeEmpty()
mei = IndexMaybeEmpty()

class Error(Base,md.Error):
    def map(self,fn):
        return self
    def chain(self,fn):
        return self.value
    def __add__(self,other):
        return other if not isinstance(other,Error) else []

def unit(x):
    return [x]
class Result(Base,md.Result):
    # def bind(self,fn):
    #     return super(Result,self).bind( r.compose(r.if_else(r.isinstance(Exception),Error,Result),excepting( fn ) ) )
    def map(self,fn):
        return Result(fn(self.value))
    def chain(self,fn):
        return fn(self.value)
    def __add__(self,other):
        return Result(self.value + other.value) if not isinstance(other,Error) else self

#Result = md.Result

ex = MethodAp(lambda x: x, r.if_else( r.isinstance(Exception), Error, Result ), excepting )
em = MethodAp(lambda x: x, r.if_else( lambda x: len(x)==0, r.always(Nothing), Just ) )
en = MethodAp(lambda x: x, r.if_else( lambda x: x is None, r.always(Nothing), Just ) )
p = MethodAp(lambda x: x, lambda x: x)
itex = IterableAp(lambda x: x, r.if_else( r.isinstance(Exception), Error, Result ), excepting )
item = IterableAp(lambda x: x, r.if_else( lambda x: len(x)==0, r.always(Nothing), Just ) )
iten = IterableAp(lambda x: x, r.if_else( lambda x: x is None, r.always(Nothing), Just ) )
it = IterableAp(lambda x:x, lambda x: x)
sc = ScalarAp(lambda x:x, lambda x: x)
scex = ScalarAp(lambda x: x, r.if_else( r.isinstance(Exception), Error, Result ), excepting  )
#foo = mn.bind( r.map(  r.compose(  mn.bind( r.map( me.find('a') ) ),mn.find_all('td') ) ) )

except_resolver = r.if_else( r.isinstance(Exception), Error, Result )
maybe_none_resolver = r.if_else( lambda x: x is None, r.always(Nothing), Just )
maybe = r.if_else( lambda x: isinstance(x,Exception) or (x is None) or (len(x)==0 if hasattr(x,'__len__') else False), r.always(Nothing),Just )
p.bind( maybe_none_resolver ).bind( except_resolver )

m = MethodAp(lambda x: x, maybe, excepting )
mit = IterableAp(lambda x: x, maybe, excepting )

out = ex.find_all('tr')(at3)
out2 = ex.bind( itex.ap( em.find_all('td').bind( item.ap( en.find('a') ) ) ) )(out)

get_title = ex.bind( itex.ap( em.find_all('td').bind( itex.ap( p.find('a').get('title') ) ) ) )


# out2 = en.bind( iten.ap( en.find_all('td') ).ap( en.bind( lambda x: len(x) ) ) )(out)

# .ap( em.bind( en.find('a') )  ) 
# out2 = p.bind( iten.ap( em.find_all('td') ) )(out)


#sc.map( except_resolver ).map( en.bind(maybe_none_resolver) )( 1 )


# map( res1 )


#sc.ap( maybe_none_resolver ).map( except_resolver )( None )


#baz = m.find_all('tr').bind( p.bind( mit.ap( em.find_all('td').bind( mit.ap( p.find('a').get('title')  ) ) )  )  )(at3)

get_titles = mit.ap( p.find('a').get('title') )
get_texts = mit.ap( p.get_text() )
get_data_rows = m.find_all('td').chain( lambda x: get_titles ) 
get_header_rows = m.find_all('th').chain( get_texts )
good_headers = m.find_all('tr').chain( mit.ap( get_header_rows ) ).chain( r.reduce(r.add,Nothing) )
good_data = m.find_all('tr').chain( mit.ap( get_data_rows ) )




from collections import namedtuple

def fmap(f, data):
    #print(type(data))
    if isinstance(data,bs4.element.ResultSet):
        result = [f(x) for x in data] 
        return bs4.element.ResultSet(data.source, result )
    if isinstance(data, dict):
        return type(data)( [(k,f(v)) for (k, v) in data.items()] )
    if isinstance(data, Just):
        return type(data)(f(data.value))
    if isinstance(data,Result):
        return type(data)(f(data.value))
    if isinstance(data,Exception):
        return type(data)(f(data.value))
    if isinstance(data, list):
        print('here')
        return type(data)(f(x) for x in data)
    return data


def cata(f, data):
    # First, we recurse inside all the values in data
    cata_on_f = lambda x: cata(f, x)
    recursed = fmap(cata_on_f, data)
    # Then, we apply f to the result
    return f(recursed)

def cata2(f, xy):
    # First, we recurse inside all the values in data
    cata_on_f = lambda xy: cata2(r.apply(f), xy)
    recursed = fmap(cata_on_f, data)
    # Then, we apply f to the result
    return f(recursed)

tagfn = lambda fn: r.if_else(r.isinstance(bs4.element.Tag),fn,r.identity)
scalarfn = lambda fn: r.if_else(r.isinstance(list),r.identity,maybe_none_resolver)

data = cata(tagfn(me.find_all('tr')),at3)
data2 = cata(tagfn(me.find_all('td')), data)
data_texts = cata(tagfn(mn.get_text()), data2 )
data3 = cata(tagfn(mn.find('a')), data2 )
data_titles = cata(tagfn(mn.get('title')), data3 )
data_links = cata(tagfn(mn.get('href')), data3 )
#data5 = cata(tagfn(maybe_none_resolver),data4)

uw_titles = cata(lambda x: x.value if isinstance(x,md.Maybe) else x, data_titles)
uw_texts = cata(lambda x: x.value if isinstance(x, md.Maybe) else x, data_texts)
w_titles = cata(r.if_else(r.isinstance(list),r.identity,r.compose(md.First,maybe_none_resolver)), uw_titles )
w_texts = cata(r.if_else(r.isinstance(list),r.identity, maybe_none_resolver), uw_texts )

out = cata( r.if_else(lambda x: True if isinstance(x,tuple) and isinstance(x[0],md.Container) else False, r.apply(r.add),r.identity),  (w_titles,w_texts) )

out2 = cata( r.if_else(r.isinstance(md.First), lambda x: x.value.value, r.identity ), out )
out3 = cata( r.if_else(r.isinstance(md.Just), lambda x: x.value, r.identity ), out2 )