# AST.py : Abstract Syntax Tree class definitions for use in MicroTree.py
# This file contains all classes necessary to build an AST for the MicroScala language.
# Author : Jo
# License : Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)

# Creates an instance of a Program class, used by MicroTree.compilationUnit, MicroTree.mainDef, and
# MicroTree.functionDef
class Program(object):
	def __init__(self, name, stmt, argList = [], funcList=[], decVarList=[]):
		self.name = name
		self.stmt = stmt
		self.argList = argList
		self.funcList = funcList
		self.decVarList = decVarList

	# Creates a string to represent the class instance when printing it out
	def __repr__(self):
		string = '\n\n'
		string += 'Abstract Syntax Tree for ' + self.name + '\n'
		string += '-------------------------'
		string += '-'*len(self.name) + '\n'

		if type(self.argList) == type(list()):
			if len(self.argList) > 0:
				string += 'Arg List\n'
				string += '--------\n'
				for count, arg in enumerate(self.argList, 1):
					if arg != None:
						string += '{0} of {1}: {2}\n'.format(str(count), len(self.argList), repr(arg))


		if type(self.decVarList) == type(list()):
			if len(self.decVarList) > 0:
				string += '\nDecl Var List\n'
				string += '-------------\n'
				for count, var in enumerate(self.decVarList, 1):
					if var != None:
						string += '{0} of {1}: {2}\n'.format(str(count), len(self.decVarList), repr(var))

		if len(self.funcList) > 0:
			string += '\nFunction List\n'
			string += '-------------\n'
			for count, func in enumerate(self.funcList, 1):
				if func != None:
					string += '{0} of {1}: {2}\n'.format(str(count), len(self.funcList), func.name)

			for func in self.funcList:
				if func != None:
					string += repr(func)

		string += '\n' + repr(self.stmt) + '\n'
		return string

# Creates an instance of a DecVar class, used by MicroTree.mainDef, MicroTree.functionDef, and
# MicroTree.varDef
class DecVar(object):
	def __init__(self, name, typ, value):
		self.name = name
		self.type = typ
		self.value = value

	# Creates a string to represent the class instance when printing it out
	def __repr__(self):
		return self.name + ' is type ' + self.type + ' := ' + str(self.value.value)

# Creates an instance of a Statement class, used by MicroTree.statement
class Statement(object):
	def __init__(self, stmt, stmt2=None):
		self.stmt = stmt
		self.stmt2 = stmt2

	# Creates a string to represent the class instance when printing it out
	def __repr__(self):
		if self.stmt2 == None:
			string = '(' + repr(self.stmt) + ')'
		else:
			string = '(: ' + repr(self.stmt) + ' ' + repr(self.stmt2) + ')'
		return string

# Creates an instance of an Expr class, used by MicroTree.expr, MicroTree.andExpr, MicroTree.relExpr,
# MicroTree.listExpr, MicroTree.addExpr, MicroTree.mulExpr, MicroTree.prefixExpr, and
# MicroTree.simpleExpr
class Expr(object):
	def __init__(self, op, term1, term2=None):
		self.op = op
		self.term1 = term1
		self.term2 = term2

	# Creates a string to represent the class instance when printing it out
	def __repr__(self):
		if self.op is not None:
			string = '(' + repr(self.op) + ' ' + repr(self.term1)
			if self.term2 is not None:
				string += ' ' + repr(self.term2)
			string += ')'
		else:
			string = ''
		return string

# Creates an instance of an If class, used by MicroTree.statement
class If(object):
	def __init__(self, cond, term1, term2=None):
		self.name = 'if'
		self.cond = cond
		self.term1 = term1
		self.term2 = term2

		if self.term2 != None:
			self.name += '-else'

	# Creates a string to represent the class instance when printing it out
	def __repr__(self):
		string = '(' + repr(self.name) + ' ' + repr(self.cond) + ' ' + repr(self.term1)
		if self.term2 != None:
			string += ' ' + repr(self.term2)
		string += ')'
		return string

# Creates an instance of a While class, used by MicroTree.statement
class While(object):
	def __init__(self, cond, statement):
		self.name = 'while'
		self.cond = cond
		self.statement = statement

	# Creates a string to represent the class instance when printing it out
	def __repr__(self):
		return '(while ' + repr(self.cond) + ' ' + repr(self.statement) + ')'

# Creates an instance of a Return class, used by MicroTree.functionDef
class Return(object):
	def __init__(self, expr):
		self.name = 'return'
		self.expr = expr

	# Creates a string to represent the class instance when printing it out
	def __repr__(self):
		return '(return ' + repr(self.expr) + ')'

# Creates an instance of an Assignment class, used by MicroTree.statement
class Assignment(object):
	def __init__(self, lhs, rhs):
		self.name = 'assign'
		self.lhs = lhs
		self.rhs = rhs

	# Creates a string to represent the class instance when printing it out
	def __repr__(self):
		return '(= ' + repr(self.lhs) + ' ' + repr(self.rhs) + ')'

# Creates an instance of a Println class, used by MicroTree.statement
class Println(object):
	def __init__(self, expr):
		self.name = 'println'
		self.expr = expr

	# Creates a string to represent the class instance when printing it out
	def __repr__(self):
		return '(println ' + repr(self.expr) + ')'

# Creates an instance of a Variable class, used by MicroTree.simpleExpr and MicroTree.statement
class Variable(object):
	def __init__(self, name):
		self.name = name

	# Creates a string to represent the class instance when printing it out
	def __repr__(self):
		return '(id ' + repr(self.name) + ')'

# Creates an instance of a FunctionCall class, used by MicroTree.simpleExpr
class FunctionCall(object):
	def __init__(self, name, parameterList=[]):
		self.name = name
		self.parameterList = parameterList

	# Creates a string to represent the class instance when printing it out
	def __repr__(self):
		return '(apply ' + repr(self.name) + ' ' + str(self.parameterList) + ')'

# Creates an instance of an IntValue class, used by MicroTree.literal and MicroTree.functionDef
class IntValue(object):
	def __init__(self, value):
		self.name = 'int'
		self.value = value

	# Creates a string to represent the class instance when printing it out
	def __repr__(self):
		return '(intValue ' + repr(self.value) + ')'

# Creates an instance of a NilValue class, used by MicroTree.literal and MicroTree.functionDef
class NilValue(object):
	def __init__(self):
		self.name = 'nil'
		self.value = 'Nil'

	# Creates a string to represent the class instance when printing it out
	def __repr__(self):
		return self.value

