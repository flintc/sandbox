from .fnutil import generator, memoizer
from .argutil import flip2
from .pointfree import concat, contains, inspect, popitem
from .core import *
from dataclasses import dataclass
from typing import Generator, Any

def immutable_cache(empty):
    @generator
    def icache():
        cache = empty()
        while True:
            data = yield cache 
            cache = concat(data,cache)
    return icache

@dataclass
class Tuple:
    value: tuple
    @classmethod
    def empty(cls):
        return cls(tuple())
    @classmethod
    def of(cls,value):
        return cls((value,))
    def concat(self,y):
        return type(self)(self.value+y.value)

tcache = immutable_cache(Tuple.empty)

@dataclass
class FIFOSafeCache:
    value: Generator
    T: Any = Tuple
    @classmethod
    def empty(cls):
        return cls( tcache() )
    @classmethod
    def of(cls,value):
        x = cls( tcache() )
        x.value.send(cls.T.of(value))
        return x
    def inspect(self):
        return self.value.send(self.T.empty())
    def concat(self,value):
        self.value.send(value.inspect())
        return self
    def append(self,y):
        return self.concat(self.of(y))
    def get(self,key):
        value = self.inspect().value
        return value[key]
    def contains(self,value):
        return value in self.inspect().value
    def popitem(self):
        value = self.get().value
        self.value = tcache()
        self.value.send(self.T(value[1:]))
        return self


def memoize(n,T):
    cache = T.empty()
    memoizer(pipe(inspect,len,lt(n)),flip_binop(contains)(cache),popitem,a