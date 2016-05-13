# MicroInterp.py : MicroScala Interpreter implementation
# MicroInterp is a class to represent an interpreter for the 
# MicroScala programming language. It accepts an Scala file as
# input, tokenizes it with MicroScalaLexer and Token classes,
# builds an AST with MicroTree and AST classes, and finally
# attempts to interpret the resulting AST, returning errors and
# halting execution when appropriate.
# Author : Jo
# License : Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)

#!/usr/bin/ python

from optparse import OptionParser
import os, logging, sys
import math, copy, re

import MicroScalaLexer
from MicroTree import MicroTree
from ErrorMessage import ErrorMessage
from Token import Token

class MicroInterp(object):
	def __init__(self, _input):
		print('\nInput:\n')
		# Parse file input into AST
		self.ast = MicroTree(_input=_input)

		# Establish program environment
		self.env = {}


		print('Output:\n')
		# Interpret the AST
		self.Prog(self.ast.tree, self.env)
		
		# Uncomment to expose the environment after running
		# print('\nEnvironment: {0}'.format(self.env))

		print('')

		# Destroy program environment
		del self.env

	# Processes AST.Program tree object
	def Prog(self, tree, env):
		if tree.stmt != None:
			context = tree.name
			env[context] = {}
			for var in tree.decVarList: # register globals
				self.InitVar(var, env, context)
			self.Main(tree.stmt, env)
		else:
			ErrorMessage(message='empty file')

	# Processes AST.Main tree object
	def Main(self, tree, env):
		if tree.stmt != None:
			context = tree.name
			# print('main: ', tree.decVarList)
			for var in tree.decVarList: # register locals to main
				# print(var.__dict__)
				self.InitVar(var, env, context)

			self.Stmt(tree.stmt, env, context)
		else:
			ErrorMessage(message=tree.__dict__)

	# Initializes a Variable into the Environment with Context
	def InitVar(self, tree, env, context):
		# print(tree.__dict__)
		lhs = self.Id(tree)
		rhs = self.Val(tree.value)

		self.update_env(env = env, context = context, lhs = lhs, rhs = rhs)

	# Processes AST.Assignment tree object to place value of rhs into env[context][lhs]
	def Var(self, tree, env, context):
		if tree.name == 'assign':
			# get ID of lhs variable
			lhs = self.Id(tree.lhs) 

			# rhs is a value
			if hasattr(tree.rhs, 'value'):
				rhs = self.Val(tree.rhs)

			# rhs is expression
			elif hasattr(tree.rhs, 'op'): 
				rhs = self.Expr(tree.rhs, env, context)

			# rhs is a variable
			elif hasattr(tree.rhs, 'name') and not hasattr(tree.rhs, 'parameterList'):	
				rhs = self.Id(tree.rhs)

			# rhs is a function
			elif hasattr(tree.rhs, 'name') and hasattr(tree.rhs, 'parameterList'):	
				rhs = self.FuncHead(tree.rhs, env, context)

			# rhs is empty
			else:
				rhs = None

			self.update_env(env = env, context = context, lhs = lhs, rhs = rhs)

	# Processes AST.FunctionCall tree object
	# Checks arguments passed to function against function declaration parameter list
	# If okay, then evaluates function in new function context
	def FuncHead(self, tree, env, context):
		out = None

		# check arguments against function parameters
		if self.ArgCheck(tree.name, tree.parameterList, env, context) is True:
			out = self.FuncBody(tree, env, context)

		return out

	# Processes the body of a function call
	# Establishes new function context distinct from other versions to enable recursion
	def FuncBody(self, tree, env, context):
		if tree != None:
			# Establish new context, save context of calling function
			callerContext = context
			context = tree.name

			# Check environment for existing function environments
			count = 0
			for key in env.keys():
				if key.startswith(context):
					count += 1

			# Create new context with name as function.name + integer iff integer > 0
			if count > 0:
				context += str(count)

			# Create empty context
			if context not in env:
				env[context] = {}

			# Find appropriate function in the AST's list of functions
			for func in self.ast.tree.funcList:
				if tree.name.startswith(func.name):
					# assign value stored in param[i] to arg[i] in env[context]
					for (param, arg) in zip(tree.parameterList, func.argList):
						# rhs is variable
						if hasattr(param, 'name'):
							rhs = env[callerContext][param.name]
						# rhs is expression
						else:
							rhs = self.Expr(param, env, callerContext)

						self.update_env(env = env, context = context, lhs = arg.name, rhs = rhs)

					# register locals to function
					for var in func.decVarList:
						self.InitVar(var, env, context)

					# evaluate function
					out = self.Stmt(func.stmt, env, context)

					# destroy local function context in env
					del env[context]

					# restore context
					context = callerContext

					break

			return out

		else:
			ErrorMessage(message=tree.__dict__)

	# Check the arguments passed to a function against the arguments in function declaration
	# for correct number of args passed and the correct type of each argument passed
	def ArgCheck(self, name, parameters, env, context):
		out = True

		# Find appropriate function in the AST's list of functions
		for func in self.ast.tree.funcList:
			if func.name.startswith(name):
				# check # of args passed against # of expected args to function	
				if len(func.argList) == len(parameters):
					# type check param[i] against arg[i]
					for (param, arg) in zip(parameters, func.argList):
						check1 = str(arg.type)

						if hasattr(param, 'name'):
							check2 = str(type(env[context][param.name]).__name__)
						else:
							check2 = str(type(self.Expr(param, env, context)).__name__)

						# remove potential issues for List [ type ] checking
						check1 = re.sub(r'\s+(\[.+)?', '', check1)
						check2 = re.sub(r'\s+(\[.+)?', '', check2)

						if check1 in ['Int', 'int'] and check2 in ['int', 'Int']:
							out &= True
						elif check1 in ['list', 'List'] and check2 in ['list', 'List']:
							out &= True
						else:
							ErrorMessage(message='Data type mismatch in function {0} for {1}: Encountered {2}, Expected {3}'.format(name, arg.name, check1, check2))
				
				# too few args passed
				elif len(func.argList) > len(parameters):
					ErrorMessage(message='Not enough arguments passed to function {0}: Encountered {1}, Expected {2}'.format(name, len(func.argList), len(parameters)))

				# too many args passed
				elif len(func.argList) < len(parameters):
					ErrorMessage(message='Too many arguments passed to function {0}: Encountered {1}, Expected {2}'.format(name, len(func.argList), len(parameters)))

				break

		return out

	# Processes AST.Statement tree object
	def Stmt(self, tree, env, context):
		out = None

		# Recursive calls
		if hasattr(tree, 'stmt'):
			# One sub-stmt
			if tree.stmt != None and tree.stmt2 == None:
				out = self.Stmt(tree.stmt, env, context)
			
			# Two sub-stmts
			elif tree.stmt != None and tree.stmt2 != None:
				out = self.Stmt(tree.stmt, env, context)
				out = self.Stmt(tree.stmt2, env, context)
		
		# Variable assignment
		elif hasattr(tree, 'lhs'): 
			if tree.lhs != None and tree.rhs != None:
				self.Var(tree, env, context)
			else:
				ErrorMessage(message='Broken assignment {0}'.format(tree.__dict__))
		
		# Conditional Evaluation -- While-loop, If-statement, If-Else-statement
		elif hasattr(tree, 'cond'):
			# While-loop
			if tree.name == 'while':
				if tree.cond != None and tree.statement != None:
					while self.Cond(tree.cond, env, context) is True:
						out = self.Stmt(tree.statement, env, context)
				else:
					ErrorMessage(message='Broken while-loop {0}'.format(tree.__dict__))

			# If-statement
			elif tree.name == 'if':
				if tree.cond != None and tree.term1 != None:
					if self.Cond(tree.cond, env, context) is True:
						out = self.Stmt(tree.term1, env, context)
				else:
					ErrorMessage(message='Broken if statement {0}'.format(tree.__dict__))

			# If-Else-statement
			elif tree.name == 'if-else':
				if tree.cond != None and tree.term1 != None and tree.term2 != None:
					if self.Cond(tree.cond, env, context) is True:
						out = self.Stmt(tree.term1, env, context)
					else:
						out = self.Stmt(tree.term2, env, context)
				else:
					ErrorMessage(message='Broken if-else statement {0}'.format(tree.__dict__))

		# Expression evaluation
		elif hasattr(tree, 'op'):
			out = self.Expr(tree, env, context)

		# Println or Return
		elif hasattr(tree, 'name'):
			# Println
			if tree.name == 'println':
				if hasattr(tree.expr, 'name'):
					lhs = env[context][self.Id(tree.expr)]
				else:
					lhs = self.Expr(tree.expr, env, context)
				print(lhs)

			# Return
			elif tree.name == 'return':
				out = self.Expr(tree.expr, env, context)
		else:
			ErrorMessage(message=tree.__dict__)

		return out

	# Processes AST.Expr tree object which is a conditional statement
	# Returns a boolean value
	def Cond(self, tree, env, context):
		# Default output to False to reduce logical assignments
		out = False
		
		# Term1 is a variable with a stored value
		if hasattr(tree.term1, 'name') and not hasattr(tree.term1, 'parameterList'):
			term1 = self.access_env(tree.term1, env, context)

		# Term1 is a functionCall
		elif hasattr(tree.term1, 'name') and hasattr(tree.term1, 'parameterList'):	
			term1 = self.FuncHead(tree.term1, env, context)

		# Term1 is an expression
		elif hasattr(tree.term1, 'op'):
			term1 = self.Expr(tree.term1, env, context)

		# Term1 is malformed
		else:
			ErrorMessage(message='LHS is malformed: {0}'.format(repr(tree.term1)))

		# Term2 is a variable with a stored value
		if hasattr(tree.term2, 'name') and not hasattr(tree.term2, 'parameterList'):
			term2 = self.access_env(tree.term2, env, context)

		# Term2 is a functionCall
		elif hasattr(tree.term2, 'name') and hasattr(tree.term2, 'parameterList'):	
			term2 = self.FuncHead(tree.term2, env, context)

		# Term2 is an expression
		elif hasattr(tree.term2, 'op'):
			term2 = self.Expr(tree.term2, env, context)

		# The operation is unary
		elif tree.term2 == None:
			pass

		# Term2 is malformed
		else:
			ErrorMessage(message='RHS is malformed: {0}'.format(tree.__dict__))

		# Evaluate the conditional by appropriate operand
		if tree.op == '>=':
			if term1 >= term2:
				out = True

		elif tree.op == '>':
			if term1 > term2:
				out = True

		elif tree.op == '<=':
			if term1 <= term2:
				out = True

		elif tree.op == '<':
			if term1 < term2:
				out = True

		elif tree.op == '==':
			# Type check for both types the same
			if type(term1) == type(term2):
				# Both terms are integers
				if type(term1) == type(int()):
					if term1 == term2:
						out = True

				# Both terms are lists
				else:
					# Check lengths
					if len(term1) == len(term2):
						out = True
						# Check each pair x[i], y[i] for equality
						for (x, y) in zip(term1, term2):
							if x == y:
								out &= True

							else:
								out &= False
								break

		elif tree.op == '!=':
			# Type check for both types the same
			if type(term1) == type(term2):
				# Both terms are integers
				if type(term1) == type(int()):
					if term1 != term2:
						out = True

				# Both terms are lists
				else:
					# Check lengths
					if len(term1) == len(term2):
						# Check each pair x[i], y[i] for inequality
						for (x, y) in zip(term1, term2):
							if x != y:
								out = True
								break

					# Different list lengths
					else:
						out = True
			# Different types
			else:
				out = True

		elif tree.op == '!':
			out = not term1

		elif tree.op == '&&':
			out = term1 and term2

		elif tree.op == '||':
			out = term1 or term2

		else:
			ErrorMessage(message='Operand not supported: {0}'.format(repr(tree.op)))

		return out

	# Processes AST.Expr tree object which is a non-conditional statement
	# Returns an integer value or list
	def Expr(self, tree, env, context):
		out = []
		term1 = []
		term2 = []

		# Term1 is a long expression
		if hasattr(tree, 'term1'):
			# Term1 is a variable
			if hasattr(tree.term1, 'name') and not hasattr(tree.term1, 'parameterList'):
				term1 = self.access_env(tree.term1, env, context)

			# Term1 is a functionCall
			elif hasattr(tree.term1, 'name') and hasattr(tree.term1, 'parameterList'):	
				term1 = self.FuncHead(tree.term1, env, context)

			# Term1 is an expression
			elif hasattr(tree.term1, 'op'):
				term1 = self.Expr(tree.term1, env, context)

			# Term1 is empty
			elif tree.term1 == None:
				term1 = []

			# Term1 is malformed
			else:
				ErrorMessage(message='LHS is malformed: {0}'.format(repr(tree.term1)))

			# Term2 is a variable
			if hasattr(tree.term2, 'name') and not hasattr(tree.term2, 'parameterList'):
				term2 = self.access_env(tree.term2, env, context)

			# Term2 is a functionCall
			elif hasattr(tree.term2, 'name') and hasattr(tree.term2, 'parameterList'):	
				term2 = self.FuncHead(tree.term2, env, context)

			# Term2 is an expression
			elif hasattr(tree.term2, 'op'):
				term2 = self.Expr(tree.term2, env, context)

			# Operand is unary, not binary
			elif tree.term2 == None:
				term2 = []

			# Term2 is malformed
			else:
				ErrorMessage(message='RHS is malformed: {0}'.format(tree.__dict__))

			# Evaluate the expression by appropriate operand
			if tree.op == '+':
				out = term1 + term2

			elif tree.op == '-':
				out = term1 - term2

			elif tree.op == '*':
				out = term1 * term2

			elif tree.op == '/':
				# Check denominator for being non-zero
				if term2 != 0:
					out = term1 // term2
				else:
					ErrorMessage(message='Divide by zero error: {0}'.format(tree.__dict__))

			elif tree.op == '::':
				# Term1 is an integer
				if type(term1) is type(int()):
					# Term2 is empty
					if term2 == None:
						out = [term1]

					# Term2 is a non-empty list
					elif type(term2) is type(list()) and len(term2) > 0:
						out = [term1]
						out.extend(term2)

					# Term2 is an empty list
					elif type(term2) is type(list()) and len(term2) == 0:
						out = [term1]

					# Term2 is an integer
					else:
						out = [term1].append(term2)

				# Term1 is a list
				elif type(term1) is type(list()):
					# Term2 is empty
					if term2 == None:
						out = term1

					# Term2 is a non-empty list
					elif type(term2) is type(list()) and len(term2) > 0:
						out = term1
						out.extend(term2)

					# Term2 is an empty list
					elif type(term2) is type(list()) and len(term2) == 0:
						out = term1

					# Term2 is an integer
					else:
						out = term1.append(term2)

			elif tree.op == 'head':
				# Term1 is a list
				if type(term1) == type(list()):
					# Term1 is not empty
					if len(term1) > 0:
						out = term1[0]

					# Term1 is empty
					else:
						ErrorMessage(message='Head: List is empty')

				# Term1 is an integer
				elif type(term1) == type(int()):
					out = term1

				# Term1 is empty
				else:
					out = []

			elif tree.op == 'tail':
				# Term1 is a list
				if type(term1) == type(list()):
					# Term1 is not empty
					if len(term1) > 0:
						out = term1[1:-1]

					# Term1 is empty
					else:
						ErrorMessage(message='Tail: List is empty')

				# Term1 is an integer
				elif type(term1) == type(int()):
					out = term1

				# Term1 is empty
				else:
					out = []

			elif tree.op == 'isEmpty':
				if len(term1) == 0:
					out = True
				else:
					out = False

			elif tree.op == '!':
				out = not term1

			elif tree.op == '&&':
				out = term1 and term2

			elif tree.op == '||':
				out = term1 or term2

			elif tree.op == '==':
				if term1 == term2:
					out = True
				else:
					out = False
			else:
				ErrorMessage(message='Operand not supported: {0}'.format(repr(tree.op)))

		# Expression contains only a single variable
		elif hasattr(tree, 'name'):
			out = self.access_env(tree, env, context)

		else:
			ErrorMessage(message='Expression not supported: {0}'.format(repr(tree)))

		return out

	# Processes AST.Variable tree object
	# Returns the name of the variable
	def Id(self, tree):
		if hasattr(tree, 'name'):
			return tree.name
		else:
			ErrorMessage(message='LHS not a variable: {0}'.format(repr(tree)))

	# Processes AST.IntValue tree object
	# Returns the integer value stored in the object
	def Val(self, tree):
		if tree.name in ['int', 'Int']:
			return int(tree.value)
		else: # is an empty list
			return []

	# Updates or inserts the value of the rhs into the variable name in lhs
	# Checks the global context first before the local context
	def update_env(self, env, context, lhs, rhs):
		lhs = lhs
		rhs = rhs

		# If context does not exist in env, create it
		if context not in env:
			env[context] = {}
		
		# Check if the rhs is a valid identifier
		if MicroScalaLexer.tokens['identifier'].match(str(rhs)):
			# Check global context for existing entry of variable-name given by rhs
			if rhs in env[self.ast.tree.name]:
				# Check global context for existing entry in variable-name given by lhs
				if lhs in env[self.ast.tree.name]:
					env[self.ast.tree.name][lhs] = env[self.ast.tree.name][rhs]
				
				# No global context for lhs, use local context variable-name given by lhs
				# and global context for variable-name given by rhs
				else:
					env[context][lhs] = env[self.ast.tree.name][rhs]

			# No global context for rhs, check for existing variable-name in local context 
			elif rhs in env[context]:
				# Check global context for existing entry in variable-name given by lhs
				if lhs in env[self.ast.tree.name]:
					env[self.ast.tree.name][lhs] = env[context][rhs]

				# No global context for lhs, use local context variable-name given by lhs
				# and local context for variable-name given by rhs
				else:
					env[context][lhs] = env[context][rhs]

		# rhs is an integer value or list
		else:
			# Check global context for existing entry in variable-name given by lhs
			if lhs in env[self.ast.tree.name]:
				env[self.ast.tree.name][lhs] = rhs
			# No global context for lhs, use local context variable-name given by lhs
			else:
				env[context][lhs] = rhs

	# Accesses the value stored in the variable tree object or Int/NilValue tree object
	# Returns an integer, Nil, or list
	# Checks the global context first before the local context
	def access_env(self, tree, env, context):
		out = None

		# Tree object is a variable
		if tree.name != 'int':
			v_id = self.Id(tree)

			# Check for existence of variable name in global context
			if v_id in env[self.ast.tree.name]:
				out = env[self.ast.tree.name][v_id]
			# No global context exists, access value stored in local context variable name
			elif v_id in env[context]:
				out = env[context][v_id]

		# Tree object is a value
		else:
			out = self.Val(tree)
		
		return out

# Runs the proggram when called by itself from command-line
def main(file):
	# Create an instance of MicroInterp class with given input file
	interp = MicroInterp(_input=file)

if __name__ == '__main__':
	usage = "usage: %prog [options] SCALA_FILE"
	parser = OptionParser(usage=usage)

	parser.add_option("-d", "--debug", action="store_true",
					  help="turn on debug mode")

	(options, args) = parser.parse_args()

	if len(args) == 0:
		file = './Test1.scala'
	elif len(args) != 1:
		parser.error("Please provide required arguments: Location of scala file")
	else:
		file = args[0]

	main(file=file)