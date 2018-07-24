class Expr:
	pass

class ExprConst(Expr):
	def __init__(self, x):
		self.x = x
	def __str__(self):
		return self.x.__str__()
	def fmap(self, f):
		return self

class ExprPlus(Expr):
	def __init__(self, x, y):
		self.x = x
		self.y = y
	def __str__(self):
		return self.x.__str__() + "+" + self.y.__str__()
	def fmap(self, f):
		return ExprPlus(f(self.x), f(self.y))


def alphaExpr(e):
	if isinstance(e, ExprConst): return e.x
	elif isinstance(e, ExprPlus): return e.x + e.y


class Fix:
	def __init__(self, x):
		self.x = x
	def __str__(self):
		return "Fix<" + self.x.__str__() + ">"


def cata(a):
	return lambda x: a(x.x.fmap(cata(a)))
x = Fix(ExprPlus(Fix(ExprConst(1)), Fix(ExprPlus(Fix(ExprConst(2)), Fix(ExprConst(4)))) ) )
y = Fix( ExprPlus( Fix(ExprConst(1)), Fix(ExprConst(1)) ))
print(cata(alphaExpr)(x))
x = Fix(ExprPlus(Fix(ExprConst(1)), Fix( ExprPlus(Fix(ExprPlus(Fix(ExprConst(2)), Fix(ExprConst(4)))), Fix(ExprPlus(Fix(ExprConst(2)), Fix(ExprConst(4))))) ) )
