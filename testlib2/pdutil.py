import pandas as pd 
from dataclasses import dataclass
from typing import Any,Iterable
import functools as ft
import numpy as np
from .core import curry,reverse,compose,prop,gather

class Series:
    def __getattribute__(self,name):
        def wrapper(*args,**kwargs):
            def wrapped(obj):
                return getattr(obj,name)(*args,**kwargs)
            return wrapped
        return wrapper

S = Series()

# def filter(fn,df):
#     return df[fn(df)]

@dataclass
class DataFrameContainer:
    value: Any
    src: Any = None
    updator: Any = lambda x: x
    @classmethod
    def of(cls,value):
        return cls(pd.DataFrame([value]))
    @classmethod
    def empty(cls):
        return cls(pd.DataFrame())
    def get(self,name):
        return type(self)(prop(name,self.value), self , self.iteratee(name))
    def filter(self,fn):
        idxs = fn(self.value)
        return type(self)( self.value[idxs], self, self.iteratee(idxs) )
    def map(self,fn):
        return type(self)( fn(self.value), self.src, self.updator )
    def concat(self,other):
        return type(self)(pd.concat( (self.value,other.value)) )
    def ap(self,f):
        return f.map( self.value )
    def __repr__(self):
        return self.value.__repr__()
    def __str__(self):
        return self.value.__str__()
    def transpose(self):
        return type(self)(self.value.transpose())
    def assign(self,key,value):
        return type(self)( self.value.assign( **{key: value} ) )
    def head(self,*args):
        return type(self)(self.value.head(*args))
    def tail(self,*args):
        return type(self)(self.value.tail(*args))
    def chain(self,fn):
        return fn(self.value)
    def iteratee(self,value):
        return (lambda x: value) if isinstance(value,pd.DataFrame) else \
            (lambda x: S.assign(**{value: x})) if isinstance(value,str) else \
            (lambda x: S.update(x,filter_func=lambda y: value) ) if isinstance(value,Iterable) and isinstance(self.value,pd.DataFrame) else \
            (lambda x: S.replace(list(self.value[value]),list(x)) ) if isinstance(value,Iterable) and isinstance(self.value,pd.Series) else \
            value
    def write(self): 
        return type(self)( self.updator(self.value)(self.src.value),self.src.src,self.src.updator )


@dataclass
class ElementWiseDataFrameContainer(DataFrameContainer):
    def map(self,fn):
        return type(self)( self.value.map(fn), self.src, self.updator )
# @curry
# def map(fn,df):
#     return df.applymap(fn)

# @curry
# def filter(fn,df):
#     return df[fn(df)]

# @curry
# def assign(key,value,df):
#     return DataFrameContainer( self.value.assign( **{key: pd.Series(value).values} ) )

# def pditeratee(value):
#     ''' 
#     allows for various short-hand notations
#     '''
#     return identity if value is None \
#         else value if callable(value) \
#         else ( lambda obj: prop(k,obj)==v for k,v in pairs(value) ) if isinstance(value,Mapping) \
#         else gather(compose(prop(value),head)) if isinstance(value,str) \
#         else None

# #def sort_by()
