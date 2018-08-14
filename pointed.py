
import dataclasses as dc  
from dataclasses import dataclass 
from typing import Any
import random
import pyramda as r
import functools as ft 


@r.curry
def ap(fn,this):
    return this.ap(fn)



def curry(fn):
    @ft.wraps(fn)
    def wrapper(*arg,**kwargs):
        try:
            return fn(*arg,**kwargs)
        except TypeError as e:
            print(e)
            if hasattr(fn,'func'):
                return curry(ft.partial(fn.func,*fn.args,*arg,**fn.keywords,**kwargs))
            else:
                return curry(ft.partial(fn,*arg,**kwargs))
    return wrapper

@dataclass
class Applicative:
    value: Any
    @classmethod
    def of(cls,value):
        return cls(value)
    def ap(self,other):
        return other.map(self.value)
    def map(self,fn):
        return self.of(curry(fn)(self.value))
    def join(self):
        return self.of(self.value.value)
    def chain(self,fn):
        return self.map(fn).join()
    def sequence(self):
        return self.value.map(self.of)

@dataclass
class Traversable(Applicative):
    @classmethod
    def of(cls,value):
        return cls((value,))
    @classmethod
    def empty(cls):
        return cls(tuple())
    def __add__(self,other):
        return self.concat(other)
    def concat(self,other):
        return type(self)( self.value+other.value )
    def append(self,other):
        return self.concat(self.of(other))
    def map(self,fn):
        return type(self)( tuple(r.map(curry(fn),self.value))  )
    def sequence(self):
        return self.map( fmap(self.of) )
    def extend(self,fn):
        return self.append(fn(self))      
    def reduce(self,fn,start_value):
        return ft.reduce(  
            fn,
            self.value,
            start_value
        )  
    def traverse(self,fn):
        return ft.reduce(
            lambda acc,x: fn(x).map(lambda b: lambda bs: bs.concat(self.of(b) )).ap(acc),
            self.value,
            type(self.value[0]).of(self.empty())  
        )


class Dict(dict):
    def __iter__(self):
        return iter(self.values())

@dataclass
class Tree(Traversable):
    @classmethod
    def of(cls,value):
        return cls(Dict(value))
    @classmethod
    def empty(cls):
        return cls(Dict())
    # def map(self,fn):
    #     return type(self)( Dict( [ curry(fn)(key,val)  for key,val in self.value.items() ] )  )
    def map(self,fn):
        return type(self)( Dict( [ (key, curry(fn)(val) )  for key,val in self.value.items() ] )  )
    def append(self,**kwargs):
        return type(self)( Dict( [ (key, val)  for key,val in tuple(self.value.items())+tuple(kwargs.items()) ] )  )
    def replace(self,**kwargs):
        return type(self)( Dict( [ (key, val)  if key not in kwargs.keys() else (key, kwargs[key] ) for key,val in self.value.items() ] )  )
        

@r.curry
def fmap(fn,this):
    result = this.map(fn) if hasattr(this,'map') else this
    #print(f'result: {result} ')
    return result



@r.curry
def node_transformer(fn,data):
    print(f'f: {data!r}')
    # if not isinstance(data,Traversable) and not isinstance(data,Applicative):
    #     return fn(data)
    if isinstance(data,Traversable):
        return fn(data)
    return data

a = Applicative.of(10)
b = Applicative.of(r.add)
rand = lambda x: Applicative.of(random.random()*x)

t = Traversable( tuple(r.map(Applicative.of,(1,2,3)) ))
to = t.traverse(fmap(r.add(9)))

aps = Applicative.of( Applicative.of( Traversable( (10,11)  )) )
ts = Traversable( ( Traversable.of(9) , 8, Traversable.of(Traversable.of(1)))  )
ts2 = Traversable( ( Traversable( (9,Traversable.of(10)) ) , Traversable.of(8), Traversable.of(Traversable.of(1)))  )

ts3 = Applicative(( 
    Applicative.of( (9,) ) , 
    Applicative.of( (8,) ), 
    Applicative.of( 
        ( Applicative.of( (1,) ), )  
    )))

@r.curry
def freduce(fn,start_value,this):
    return this.reduce(fn,start_value)

@r.curry
def chain(fn,x):
    return x.chain(fn)

def extender(x):
    print(f'extender: {x}')
    #return {str(len(x.value)): x.value }
    return x

tr = Tree( Dict(a=Tree(Dict(a2=Tree(Dict(a3=-1)),b2=100)),b=7 )  )

DTree = lambda **x: Tree(Dict(**x))

tr = DTree(
    image= DTree(
        filename='foo.png',
        roi=DTree(
            x=0,
            y=0,
            w=10,
            h=10,
            children=DTree(
                esf=[],
                lsf=[],
                mtf=[]
            )
        )
    )
)

def imread(filename=None):
    print(f'{filename}' )
    return filename


def cata(f, data):
    print(f'cata: {data!r}')
    # First, we recurse inside all the values in data
    cata_on_f = lambda x: cata(f, x)
    recursed = fmap(cata_on_f, data)

    # Then, we apply f to the result
    return f(recursed)

def lin_cata(f,data):
    def cata0(f,data):
        cata_on_f = lambda x: cata0(f, x)
        recursed = fmap(cata_on_f, data)
        yield f(recursed)
    gen = cata0(f,data)
    return next(gen)

'''
export type Coalgebra<F, A> = A => HKT<F, A>;
export function ana<F, A>(functor: Functor<F>,
                          transformer: Coalgebra<F, A>,
                          seed: A) : Fix<F> {
  const transformed = transformer(seed),
        childrenMapped = functor.map(
          x => ana(transformer, x, functor),
          transformed),
        rewrapped = new In(childrenMapped);
  return rewrapped;
}

export function hylo<F, A, B>(functor: Functor<F>,
                              algebra: Algebra<F, B>,
                              coalgebra: Coalgebra<F, A>,
                              seed: A) : B {
  const builtUp = coalgebra(seed),
        mapped = functor.map(
          x => hylo(functor, algebra, coalgebra, x), builtUp),
        flattened = algebra(mapped);
  return flattened;
}
'''

terminator = lambda x: not hasattr(x,'map')

@r.curry
def ana(transformer,seed):
    transformed = transformer(seed)
    children_mapped = transformed.map( ana(terminator,transformer) ) if not terminator(seed) else seed
    return children_mapped

@r.curry 
def hylo(count,end_cond,tear_down,build_up,seed):
    built_up = build_up(seed)
    mapped = fmap( hylo(count+1,end_cond,tear_down,build_up), built_up ) if not end_cond(seed) and count<3 else seed
    flattened = tear_down(mapped)
    return flattened

def builder(level):
    DTree(Dict(src=level.value['resolver'],  ))

def print_a(x):
    print(f'a!: {x!r}' )
    print(len(inspect.stack()))
    return x 
def print_b(x):
    print(f'b!: {x!r}' )
    print(len(inspect.stack()))
    return x 

tr2 = DTree(
    resolver=print_b,
    children= DTree(
        resolver=print_a,
        arg=DTree(
            resolver=print_b,
            arg1=0,
            arg2=10,
            arg3=10,
            children=DTree(
                resolver=print_a,
                arg1=[],
                arg2=[]
            )
        )
    )
)
import inspect
def fn(x):
    print(len(inspect.stack()))
    return x
import itertools as it  
counter = it.count()

def bu(x):
    #print(f'bu: {type(x)}')
    if isinstance(x,Tree):
        print(f"{' '*len(inspect.stack())} BUILDING up: {type(x)},{x!r}, stack len: {len(inspect.stack())}")
        return x
        #for k,v in x
        #return (x.value['resolver'], x)
        #x.value['resolver']('here!')
        # if hasattr(x.value,'src'):
        #     print('composing')
        #     x.value['src'] = r.compose(x.value['src'],x.value['resolver'])
        # else:
        #     x.value['src'] = x.value['resolver']
        #return x
    else:
        return x

def td(x):
    #print(f'bu: {type(x)}')
    if isinstance(x,tuple):
        print(f"{' '*len(inspect.stack())} tearing DOWN: {type(x)}, stack len: {len(inspect.stack())}")
        x('here?')
        return x
    elif isinstance(x,Tree):
        print(f"{' '*len(inspect.stack())} tearing DOWN: {type(x)}, stack len: {len(inspect.stack())}")
        print(x.value.keys())
        return x
    # elif isinstance(x,Dict):
    #     print('here!')
    #     return x 
    else:
        return x

def keyed(key,value,transformer):
    print(f'{key}: !! {value}')
    return transformer(value)


def resolve(*val):
    print(val)
    return ( val[0]+' 1 ', val[1] )



five_deep = Applicative.of(
    Applicative.of(
        Applicative.of(
            Applicative.of(
                Applicative.of(1)
            )
        )
    )
)

fd_dict = DTree(
    a=DTree(a20=100),
    b=DTree(
        a2=10,
        b2=DTree(
            c3=-1,
            a3=DTree(
                a4='hi'
            )
        )
    )
)

IV = lambda x: x
DV = lambda fn: 

lin_dict = DTree(
    step1 = DTree(
        fn=r.add,
        x=1,
        y=2
    ),
    step2 = DTree(
        fn=r.multiply,
        y= -80
    )
)


def trampoline(f, *args):
    v = f(*args)
    while callable(v):
        print('tramp',len(inspect.stack()))
        v = v()
    while callable(v.value):
        pass
    return v
def fact_cps_thunked(n, cont):
    print(len(inspect.stack()))
    if n == 0:
        return cont(1)
    else:
        return lambda: fact_cps_thunked(
                         n - 1,
                         lambda value: lambda: cont(n * value))

end_cont = lambda value: value
#trampoline(fact_cps_thunked, 6, end_cont)



@r.curry
def rmap(fn,this):
    result = this.map(fn) if hasattr(this,'map') else this
    print(f'result: {result} ')
    return result

def lcata(f, data):
    # First, we recurse inside all the values in data
    cata_on_f = lambda x: lcata(f, x)
    recursed = rmap(cata_on_f, data)
    # Then, we apply f to the result
    return lambda *x: f(recursed)


def unwrap(x):
    v = x
    y = ()
    while callable(v.value):
        v = v.value()
        
