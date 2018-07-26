
from functools import wraps,partial
import pyramda as r
# that(x)(this(x))
def tap(fn):
    def wrapper(x):
        fn(x)
        return x 
    return wrapper

def thru(fn):
    def wrapper(x):
        return fn(x)
    return wrapper

def add(x,y):
    return x+y


def part(fn,arg):
    return partial(fn,arg)

class Fn(object):
    @classmethod
    def of(cls,fn):
        return cls(lambda *x: fn)
    @classmethod
    def constructor(cls,val):
        return cls(val)
    @classmethod
    def empty(cls):
        return cls(lambda x: x)
    def __init__(self,value):
        self.value = value
    def __call__(self,*x):
        return r.apply(self.value)(x)
    def __getattr__(self,name):
        fn = globals()[name]
        def wrapper(*args,**kwargs):
            return self.fmap( r.curry(fn)(*args,**kwargs) )
        return wrapper
    def ap(self,that):
        def wrapper(x):
            return that(x)(self(x))
        return self.constructor(wrapper)
    # just like compose!!
    def fmap(self,that):
        return self.ap(self.of(that))
    def contrafmap(self,that):
        return self.constructor(that).fmap(self)
    def promap(self,before,after):
        return self.contrafmap(before).fmap(after)


def lift2(fn,f,g):
    return Fn(g).ap(Fn(f).fmap(fn))

@r.curry
def lift3(f,a,b,c):
    return c.ap(b.ap(a.fmap(f)))

@r.curry
def compose(f,g,x):
    return f(g(x))

this = lambda x: x+2
f_fn = lambda x: x*10
g_fn = lambda x: x/100
test_val = 10
def assert_equals(a,b):
    try:
        assert(a==b)
        print('a==b? True. a: {}, b: {}'.format(a,b))
    except AssertionError:
        print('a==b? False. a: {}, b: {}'.format(a,b))
#identity
def map_id():
    x = Fn(this)
    f = f_fn 
    a = x.fmap(r.identity)(test_val) 
    b = x(test_val) 
    assert_equals(a,b)

#composition
def map_comp():
    f = f_fn
    g = g_fn 
    x = Fn(this)
    a = x.fmap(f).fmap(g)(test_val)
    b = x.fmap( lambda x: g(f(x)) )(test_val) 
    assert_equals(a,b)

#### ap
#composition
def ap_composition():
    x = Fn(this)
    g = Fn.of(g_fn)
    f = Fn.of(f_fn)
    a = x.ap(g.ap(f.fmap(compose)))(test_val)
    print('a: {}'.format(a))
    b = x.ap(g).ap(f)(test_val)
    print('b: {}'.format(b))
    assert_equals(a,b)
    #assert(  lift3(r.compose)(f)(g)(x)(test_val) == x.ap(g).ap(f)(test_val) )


# / Identity.
# v.ap(A.of(x => x)) === v

# // Homomorphism
# A.of(x).ap(A.of(f)) === A.of(f(x))

# // Interchange
# A.of(y).ap(u) === u.ap(A.of(f => f(y)))

#### of
def of_id():
    v = Fn(this)
    a = v.ap(Fn.of(r.identity))(test_val)
    b = v(test_val)
    assert_equals(a,b)

def of_homomorphism():
    x = test_val 
    f = f_fn 
    a = Fn.of(x).ap(Fn.of(f))(test_val)
    b = Fn.of(f(x))(test_val)
    assert_equals(a,b)

map_id()
map_comp()
ap_composition()
of_id()
of_homomorphism()


tap_before = tap(lambda x: print('before: {}'.format(x))) 
tap_after = tap(lambda x: print('after: {}'.format(x) )) 

out = Fn(this) \
    .fmap( tap_after ) \
    .contrafmap(tap_before )(10)

out = Fn(this) \
    .contrafmap( tap_before ) \
    .fmap( tap_after )(10)

out = Fn(this).promap(tap_before, tap_after)
