# MicroScala Abstract Tree implementation
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
import math, copy
from MicroScalaLexer import MicroScalaLexer
from ErrorMessage import ErrorMessage
from Token import Token, UNDEFINED
import AST

sys.setrecursionlimit(10000)

class MicroTree(object):
	def __init__(self, _input):
		self.token = Token(symbol='start', lexeme='start')
		self.lexer = MicroScalaLexer(_input=_input)

		self.getToken()
		self.tree = self.program()

	# getToken() : input: None, output: None
	# Obtains the next token from the lexer
	def getToken(self):
		self.token = self.lexer.nextToken()

		# Skips epsilon and comment tokens
		while(self.token.symbol() == 'e' or self.token.symbol() == 'comment'):

			self.token = self.lexer.nextToken()

	# program() : input: None, output: instance of AST.Program()
	# Recognizes the following BNF where symbols preceded with underscores are in-language symbols
	# EOF was added to represent the end-of-file -- returned by lexer when input file is fully parsed
	# compilationUnit ::= object id _{ {def} mainDef _} EOF
	def program(self):
		function = prgm = main = None
		symbol = ''
		argList = []
		funcList = []
		decVarList = []
		name = ''

		# object
		if self.token.symbol() != 'object':
			ErrorMessage('{0} expected'.format('object'), self.lexer.position(), self.lexer.echo())
		
		self.getToken()
		
		# identifier
		if self.token.symbol() != 'identifier':
			ErrorMessage('{0} expected'.format('id'), self.lexer.position(), self.lexer.echo())

		# store identifer in name
		name = self.token.lexeme()
		self.getToken()
		
		# _{
		if self.token.symbol() != 'leftbrace':
			ErrorMessage('{0} expected'.format('{'), self.lexer.position(), self.lexer.echo())
		
		self.getToken()
		
		# {def}
		# Cycles through optional function and global variable declarations until 'def main' is reached
		while symbol != 'main':
			symbol, function = self.functionDef(name = name)
			if symbol != 'main' and function != None:
				# Check type of function
				if function.name != name and type(function) != type(AST.DecVar(name='',typ='',value='')):
					# function is a function AST.Program()
					funcList.append(function)
				else:
					# function is a declared variable AST.DecVar()
					decVarList.append(function)

		# mainDef
		main = self.mainDef(symbol)

		# _}
		if self.token.symbol() != 'rightbrace':
			ErrorMessage('{0} expected'.format('}'), self.lexer.position(), self.lexer.echo())
		
		self.getToken()

		# EOF
		if self.token.symbol() != 'EOF':
			ErrorMessage('{0} expected'.format('EOF'), self.lexer.position(), self.lexer.echo())			
		
		# Create new instance of class AST.Program()
		prgm = AST.Program(name = name, stmt = copy.deepcopy(main), argList = copy.deepcopy(argList), funcList = copy.deepcopy(funcList), decVarList = copy.deepcopy(decVarList))
		
		return prgm

	# mainDef() : input: symbol -- str(), output: instance of AST.Program()
	# Recognizes the following BNF where symbols preceded with underscores are in-language symbols
	# mainDef ::= def main ( args : Array _[ String _] ) _{ {varDef} statement {statement} _}
	def mainDef(self, symbol):
		prgm = None
		stmt1 = stmt2 = None
		argList = []
		decVarList = []
		arg = ''
		typ = ''

		# def
		if self.token.symbol() == 'def':
			self.getToken()

		# main
		# Rejects identifier that is not main and raises error
		if self.token.symbol() != 'main' and symbol != 'main':
			ErrorMessage('{0} expected'.format('main'), self.lexer.position(), self.lexer.echo())
		
		self.getToken()
		
		# (
		if self.token.symbol() == 'leftparen':
			self.getToken()

			# args
			if self.token.symbol() != 'args':
				ErrorMessage('{0} expected'.format('Args'), self.lexer.position(), self.lexer.echo())
			
			# store args lexeme in args
			arg = self.token.lexeme()
			self.getToken()
			
			# :
			if self.token.symbol() != 'colon':
				ErrorMessage('{0} expected'.format(':'), self.lexer.position(), self.lexer.echo())
			
			self.getToken()
			
			# Array
			if self.token.symbol() != 'array':
				ErrorMessage('{0} expected'.format('Array'), self.lexer.position(), self.lexer.echo())
			
			# store type of args in typ
			typ = self.token.lexeme()
			self.getToken()
			
			# [
			if self.token.symbol() != 'leftbracket':
				ErrorMessage('{0} expected'.format('['), self.lexer.position(), self.lexer.echo())
			
			typ += ' ' + self.token.lexeme()
			self.getToken()
			
			# String
			if self.token.symbol() != 'string':
				ErrorMessage('{0} expected'.format('String'), self.lexer.position(), self.lexer.echo())
			
			typ += ' ' + self.token.lexeme()
			self.getToken()
			
			# ]
			if self.token.symbol() != 'rightbracket':
				ErrorMessage('{0} expected'.format(']'), self.lexer.position(), self.lexer.echo())
			
			typ += ' ' + self.token.lexeme()
			self.getToken()
			
			# )
			if self.token.symbol() != 'rightparen':
				ErrorMessage('{0} expected'.format(')'), self.lexer.position(), self.lexer.echo())
			
			self.getToken()

		# _{
		if self.token.symbol() != 'leftbrace':
			ErrorMessage('{0} expected'.format('{'), self.lexer.position(), self.lexer.echo())
		
		self.getToken()

		# {varDef}
		while self.token.symbol() == 'var':
			var = self.varDef()
			if var != None:
				decVarList.append(var)

		# statement
		stmt1 = self.statement()

		# {statement}
		while self.token.symbol() != 'rightbrace':
			stmt2 = self.statement()
			stmt1 = AST.Statement(copy.deepcopy(stmt1), copy.deepcopy(stmt2))

		# _}
		if self.token.symbol() != 'rightbrace':
			ErrorMessage('{0} expected'.format('}'), self.lexer.position(), self.lexer.echo())

		self.getToken()

		argList.append(AST.DecVar(name = arg, typ = typ, value = AST.NilValue()))

		prgm = AST.Program(name = 'main', stmt = copy.deepcopy(stmt1), argList = copy.deepcopy(argList), funcList = [], decVarList = copy.deepcopy(decVarList))
		
		return prgm

	# functionDef() : input: name -- str(), output: symbol -- str(), instance of AST.Program()
	# Recognizes the following BNF where symbols preceded with underscores are in-language symbols
	# def ::= def id ( [id : Type {, id : Type } ] ) : Type = _{ {varDef} {statement} return listExpr ; _}
	#        | varDef
	def functionDef(self, name):
		symbol = 'def'
		funcId = ''
		expr = None
		stmt1 = stmt2 = None
		prgm = None
		rtrn = None
		decVarList = []
		argList = []
		arg = None
		name = ''
		typ = ''

		# def
		if self.token.symbol() == 'def':
			self.getToken()

			# identifier that is not main
			if self.token.symbol() == 'identifier' and self.token.lexeme() != 'main':
				# store lexeme in funcId
				funcId = self.token.lexeme()
				self.getToken()

				# (
				if self.token.symbol() != 'leftparen':
					ErrorMessage('{0} expected'.format('('), self.lexer.position(), self.lexer.echo())
				
				self.getToken()

				# id -- identifier of 1st declared argument to pass to function
				if self.token.symbol() == 'identifier':
					# store argument id into name
					name = self.token.lexeme()
					self.getToken()

					# :
					if self.token.symbol() != 'colon':
						ErrorMessage('{0} expected'.format(':'), self.lexer.position(), self.lexer.echo())
					
					self.getToken()

					# Type -- store argument type into typ
					typ = self.type()

					# if argument is Int, create DecVar with default int value UNDEFINED
					if typ in ['int', 'Int']:
						arg = AST.DecVar(name = name, typ = typ, value = AST.IntValue(value = UNDEFINED))
					# else argument is Array -- treat as List with default Nil value
					else:
						arg = AST.DecVar(name = name, typ = typ, value = AST.NilValue())

					# add argument to argument list
					argList.append(arg)

					# ,
					while self.token.symbol() == 'comma':
						self.getToken()

						# id -- identifier of 2nd+ declared argument to pass to function
						if self.token.symbol() != 'identifier':
							ErrorMessage('{0} expected'.format('id'), self.lexer.position(), self.lexer.echo())
						
						# store argument id into name
						name = self.token.lexeme()
						self.getToken()

						# :
						if self.token.symbol() != 'colon':
							ErrorMessage('{0} expected'.format(':'), self.lexer.position(), self.lexer.echo())
						
						self.getToken()

						# Type -- store argument type into typ
						typ = self.type()

						# if argument is Int, create DecVar with default int value UNDEFINED
						if typ in ['int', 'Int']:
							arg = AST.DecVar(name = name, typ = typ, value = AST.IntValue(value = UNDEFINED))
						# else argument is Array -- treat as List with default Nil value
						else:
							arg = AST.DecVar(name = name, typ = typ, value = AST.NilValue())

						# add argument to argument list
						argList.append(arg)

				# )
				if self.token.symbol() != 'rightparen':
					ErrorMessage('{0} expected'.format(')'), self.lexer.position(), self.lexer.echo())
				
				self.getToken()

				# :
				if self.token.symbol() != 'colon':
					ErrorMessage('{0} expected'.format(':'), self.lexer.position(), self.lexer.echo())
				
				self.getToken()

				# Type
				self.type()

				# =
				if self.token.symbol() != 'assign':
					ErrorMessage('{0} expected'.format('='), self.lexer.position(), self.lexer.echo())
				
				self.getToken()

				# _{
				if self.token.symbol() != 'leftbrace':
					ErrorMessage('{0} expected'.format('{'), self.lexer.position(), self.lexer.echo())
				
				self.getToken()

				# {varDef}
				while self.token.symbol() == 'var':
					var = self.varDef()
					if var != None:
						decVarList.append(var)

				# {statement}
				while self.token.symbol() != 'return':
					stmt2 = self.statement()

					if stmt1 == None:
						stmt1 = stmt2
					else:
						stmt1 = AST.Statement(stmt = copy.deepcopy(stmt1), stmt2 = copy.deepcopy(stmt2))

				# return
				if self.token.symbol() != 'return':
					ErrorMessage('{0} expected'.format('return'), self.lexer.position(), self.lexer.echo())

				self.getToken()
				
				# listExpr
				expr = self.listExpr()

				# Create instance of AST.Return() object
				rtrn = AST.Return(expr = copy.deepcopy(expr))

				if stmt1 == None:
					stmt1 = rtrn
				else:
					stmt1 = AST.Statement(stmt = copy.deepcopy(stmt1), stmt2 = copy.deepcopy(rtrn))

				# ;
				if self.token.symbol() != 'semicolon':
					ErrorMessage('{0} expected'.format(';'), self.lexer.position(), self.lexer.echo())

				self.getToken()

				# _}
				if self.token.symbol() != 'rightbrace':
					ErrorMessage('{0} expected'.format('}'), self.lexer.position(), self.lexer.echo())

				self.getToken()

				prgm = AST.Program(name = funcId, stmt = copy.deepcopy(stmt1), argList = copy.deepcopy(argList), funcList = [], decVarList = copy.deepcopy(decVarList))

			else:
				symbol = 'main'

		# varDef
		else:
			decVarList = self.varDef()

			prgm = decVarList

		return symbol, prgm

	# varDef() : input: None, output: instance of AST.DecVar()
	# Recognizes the following BNF where symbols preceded with underscores are in-language symbols
	# VarDef ::= var id : Type = Literal ;
	def varDef(self):
		var = None

		# var
		if self.token.symbol() == 'var':
			self.getToken()

			# id
			if self.token.symbol() != 'identifier':
				ErrorMessage('{0} expected'.format('id'), self.lexer.position(), self.lexer.echo())

			# store variable id in v_id
			v_id = self.token.lexeme()

			self.getToken()

			# :
			if self.token.symbol() != 'colon':
				ErrorMessage('{0} expected'.format(':'), self.lexer.position(), self.lexer.echo())

			self.getToken()

			# Type -- store variable type into v_type
			v_type = self.type()

			# =
			if self.token.symbol() != 'assign':
				ErrorMessage('{0} expected'.format('='), self.lexer.position(), self.lexer.echo())

			self.getToken()

			# Literal -- store variable value into v_val
			v_val = self.literal()

			# ;
			if self.token.symbol() != 'semicolon':
				ErrorMessage('{0} expected'.format(';'), self.lexer.position(), self.lexer.echo())

			self.getToken()

			var = AST.DecVar(name = v_id, typ = v_type, value = v_val)

		return var

	# type() : input: None, output: typ -- str() representing type of variable
	# Recognizes the following BNF where symbols preceded with underscores are in-language symbols
	# Type ::= Int | List _[ Int _]
	def type(self):
		typ = None

		# Int
		if self.token.symbol() == 'int':
			typ = self.token.lexeme()
			self.getToken()
		
		# List
		elif self.token.symbol() == 'list':
			typ = self.token.lexeme()
			self.getToken()

			# _[
			if self.token.symbol() != 'leftbracket':
				ErrorMessage('{0} expected'.format('['), self.lexer.position(), self.lexer.echo())
			
			self.getToken()
			
			# Int
			if self.token.symbol() != 'int':
				ErrorMessage('{0} expected'.format('Int'), self.lexer.position(), self.lexer.echo())
			
			typ += ' [' + self.token.lexeme() + ']'
			self.getToken()

			# _]
			if self.token.symbol() != 'rightbracket':
				ErrorMessage('{0} expected'.format(']'), self.lexer.position(), self.lexer.echo())
			
			self.getToken()

		else:
			ErrorMessage('{0} expected'.format('type'), self.lexer.position(), self.lexer.echo())

		return typ

	# statement() : input: None, output: instance of appropriate AST object
	# Recognizes the following BNF where symbols preceded with underscores are in-language symbols		
	# Statement ::= if ( Expr ) Statement [ else Statement]
	# 			| while ( Expr ) Statement 
	# 			| id = ListExpr ;
	# 			| println ( ListExpr ) ;
	# 			| _{ Statement { Statement } _}
	def statement(self):
		expr = None
		stmt = stmt1 = stmt2 = None
		v_id = None

		# if
		if self.token.symbol() == 'if':
			self.getToken()

			# (
			if self.token.symbol() != 'leftparen':
				ErrorMessage('{0} expected'.format('('), self.lexer.position(), self.lexer.echo())
			
			self.getToken()

			# Expr -- store Expr into expr
			expr = self.expr()

			# )
			if self.token.symbol() != 'rightparen':
				ErrorMessage('{0} expected'.format(')'), self.lexer.position(), self.lexer.echo())
			
			self.getToken()

			# Statement
			stmt1 = self.statement()

			# [ else Statement ]
			if self.token.symbol() == 'else':
				self.getToken()
				stmt2 = self.statement()

			stmt = AST.If(cond = copy.deepcopy(expr), term1 = copy.deepcopy(stmt1), term2 = copy.deepcopy(stmt2))

		# while
		elif self.token.symbol() == 'while':
			self.getToken()

			# (
			if self.token.symbol() != 'leftparen':
				ErrorMessage('{0} expected'.format('('), self.lexer.position(), self.lexer.echo())
			
			self.getToken()
			
			# Expr -- store Expr into expr
			expr = self.expr()

			# )
			if self.token.symbol() != 'rightparen':
				ErrorMessage('{0} expected'.format(')'), self.lexer.position(), self.lexer.echo())
			
			self.getToken()

			# Statement
			stmt1 = self.statement()

			stmt = AST.While(cond = copy.deepcopy(expr), statement = copy.deepcopy(stmt1))

		# id
		elif self.token.symbol() == 'identifier':
			v_id = AST.Variable(name = self.token.lexeme())

			self.getToken()

			# =
			if self.token.symbol() != 'assign':
				ErrorMessage('{0} expected'.format('='), self.lexer.position(), self.lexer.echo())

			self.getToken()

			# ListExpr -- store ListExpr into expr
			expr = self.listExpr()

			# ;
			if self.token.symbol() != 'semicolon':
				ErrorMessage('{0} expected'.format(';'), self.lexer.position(), self.lexer.echo())
			
			self.getToken()

			stmt = AST.Assignment(lhs = v_id, rhs = copy.deepcopy(expr))

		# println
		elif self.token.symbol() == 'println':
			self.getToken()

			# (
			if self.token.symbol() != 'leftparen':
				ErrorMessage('{0} expected'.format('('), self.lexer.position(), self.lexer.echo())
			
			self.getToken()

			# ListExpr -- store ListExpr into expr
			expr = self.listExpr()
			
			# )
			if self.token.symbol() != 'rightparen':
				ErrorMessage('{0} expected'.format(')'), self.lexer.position(), self.lexer.echo())
			
			self.getToken()

			# ;
			if self.token.symbol() != 'semicolon':
				ErrorMessage('{0} expected'.format(';'), self.lexer.position(), self.lexer.echo())
			
			self.getToken()

			stmt = AST.Println(expr = copy.deepcopy(expr))

		# _{
		elif self.token.symbol() == 'leftbrace':
			self.getToken()

			# Statement
			stmt1 = self.statement()

			# {Statement}
			while self.token.symbol() != 'rightbrace':
				stmt2 = self.statement()
				stmt1 = AST.Statement(copy.deepcopy(stmt1), copy.deepcopy(stmt2))

			# _}
			if self.token.symbol() != 'rightbrace':
				ErrorMessage('{0} expected'.format('}'), self.lexer.position(), self.lexer.echo())

			self.getToken()

			stmt = stmt1

		return stmt

	# expr() : input: None, output: instance of AST.Expr() object
	# Recognizes the following BNF where symbols preceded with underscores are in-language symbols	
	# expr ::= andExpr {|| andExpr}
	def expr(self):
		# andExpr
		expr = self.andExpr()
		term1 = None
		term2 = None

		# {|| andExpr}
		while self.token.symbol() == 'or':
			# ||
			op = self.token.lexeme()
			self.getToken()

			# andExpr
			andExpr = self.andExpr()

			term1 = expr
			term2 = andExpr
			expr = AST.Expr(op = op, term1 = copy.deepcopy(expr), term2 = copy.deepcopy(andExpr))

		return expr

	# andExpr() : input: None, output: instance of AST.Expr() object
	# Recognizes the following BNF where symbols preceded with underscores are in-language symbols	
	# andExpr ::= relExpr {&& relExpr}
	def andExpr(self):
		# relExpr -- store relExpr in expr
		expr = self.relExpr()

		# {&& relExpr}
		while self.token.symbol() == 'and':
			# &&
			op = self.token.lexeme()
			self.getToken()

			# relExpr
			relExpr = self.relExpr()
			expr = AST.Expr(op = op, term1 = copy.deepcopy(expr), term2 = copy.deepcopy(relExpr))

		return expr

	# relExpr() : input: None, output: instance of AST.Expr() object
	# Recognizes the following BNF where symbols preceded with underscores are in-language symbols	
	# relExpr ::= [!] listExpr [relOper listExpr]
	def relExpr(self):
		op = None

		# [!] -- store in op if exists
		if self.token.symbol() == 'not':
			op = self.token.lexeme()
			self.getToken()

		# listExpr -- store listExpr in expr
		expr = self.listExpr()

		# [relop listExpr]
		# store relOper in relop
		relop = self.relOper()

		if relop != None:
			term2 = self.listExpr()
			expr = AST.Expr(op = relop, term1 = copy.deepcopy(expr), term2 = copy.deepcopy(term2))

		if op != None:
			expr = AST.Expr(op = op, term1 = copy.deepcopy(expr), term2 = None)

		return expr

	# relOper() : input: None, output: op -- str()
	# Recognizes the following BNF where symbols preceded with underscores are in-language symbols	
	# relOper ::= < | <= | > | >= | == | !=
	def relOper(self):
		op = None

		# < | <= | > | >= | == | !=
		if self.token.symbol() == 'relop':
			op = self.token.lexeme()
			self.getToken()

		return op

	# listExpr() : input: None, output: instance of AST.Expr() object
	# Recognizes the following BNF where symbols preceded with underscores are in-language symbols
	# listExpr ::= addExpr | addExpr :: listExpr
	def listExpr(self):
		# addExpr -- store addExpr to expr
		expr = self.addExpr()

		# :: listExpr
		if self.token.symbol() == 'cons':
			op = self.token.lexeme()
			self.getToken()
			term2 = self.listExpr()

			expr = AST.Expr(op = op, term1 = copy.deepcopy(expr), term2 = copy.deepcopy(term2))

		return expr

	# addExpr() : input: None, output: instance of AST.Expr() object
	# Recognizes the following BNF where symbols preceded with underscores are in-language symbols
	# addExpr ::= mulExpr {addOper mulExpr}
	def addExpr(self):
		# mulExpr -- store mulExpr in expr
		expr = self.mulExpr()
		op = True

		# {addOper mulExpr}
		while op != None:
			# addOper
			op = self.addOper()

			# mulExpr -- store in term2, store expr into term1
			if op != None:
				term1 = expr
				term2 = self.mulExpr()
				expr = AST.Expr(op = op, term1 = copy.deepcopy(term1), term2 = copy.deepcopy(term2))

		return expr

	# addOper() : input: None, output: op -- str()
	# Recognizes the following BNF where symbols preceded with underscores are in-language symbols
	#  addOper ::= + | -
	def addOper(self):
		op = None

		# + | -
		if self.token.symbol() == 'addop':
			op = self.token.lexeme()
			self.getToken()

		return op

	# mulExpr() : input: None, output: instance of AST.Expr() object
	# Recognizes the following BNF where symbols preceded with underscores are in-language symbols
	# mulExpr ::= prefixExpr {mulOper prefixExpr}
	def mulExpr(self):
		# prefixExpr -- store prefixExpr in expr
		expr = self.prefixExpr()
		op = True

		# {mulOper prefixExpr}
		while op != None:
			# mulOper
			op = self.mulOper()

			# prefixExpr -- store in term2, store expr into term1
			if op != None:
				term1 = expr
				term2 = self.prefixExpr()
				expr = AST.Expr(op = op, term1 = copy.deepcopy(expr), term2 = copy.deepcopy(term2))

		return expr

	# addOper() : input: None, output: op -- str()
	# Recognizes the following BNF where symbols preceded with underscores are in-language symbols
	# mulOper ::= * | /
	def mulOper(self):
		op = None

		# * | /
		if self.token.symbol() == 'multop':
			op = self.token.lexeme()		
			self.getToken()
		
		return op

	# prefixExpr() : input: None, output: instance of AST.Expr() object
	# Recognizes the following BNF where symbols preceded with underscores are in-language symbols
	# prefixExpr ::= [addOper] simpleExpr {listMethodCall}
	def prefixExpr(self):
		# [addOper]
		addop = self.addOper()

		# simpleExpr -- store simpleExpr in expr
		expr = self.simpleExpr()
		listop = True

		# {listMethodCall}
		while listop != None:
			listop = self.listMethodCall()
			if listop != None:
				expr = AST.Expr(op = listop, term1 = copy.deepcopy(expr), term2 = None)

		if addop != None:
			expr = AST.Expr(op = addop, term1 = copy.deepcopy(expr), term2 = None)

		return expr

	# listMethodCall() : input: None, output: op -- str()
	# Recognizes the following BNF where symbols preceded with underscores are in-language symbols
	# listMethodCall ::= . head | . tail | . isEmpty
	def listMethodCall(self):
		op = None

		# .
		if self.token.symbol() == 'period':
			self.getToken()

			# head | tail | isEmpty -- store listOp into op
			if self.token.symbol() == 'listop':
				op = self.token.lexeme()
				self.getToken()
			else:
				ErrorMessage('{0} expected'.format('(head | tail | isempty)'), self.lexer.position(), self.lexer.echo())

		return op

	# simpleExpr() : input: None, output: instance of appropriate AST object
	# Recognizes the following BNF where symbols preceded with underscores are in-language symbols	
	# simpleExpr ::= literal | ( expr ) | id [ ( [ listExpr {, listExpr} ] ) ]
	def simpleExpr(self):
		v_id = None
		parameterList = []

		# id
		if self.token.symbol() == 'identifier':
			# store id lexeme into v_id
			v_id = self.token.lexeme()
			self.getToken()

			# [ ( ...
			if self.token.symbol() == 'leftparen':
				self.getToken()

				# listExpr -- store listExpr into parameterList
				parameterList.append(copy.deepcopy(self.listExpr()))

				# { , ...
				while self.token.symbol() == 'comma':
					self.getToken()
					# listExpr -- store listExpr into parameterList
					parameterList.append(copy.deepcopy(self.listExpr()))

				# ) ]
				if self.token.symbol() != 'rightparen':
					ErrorMessage('{0} expected'.format(')'), self.lexer.position(), self.lexer.echo())					
				
				self.getToken()

				expr = AST.FunctionCall(name = v_id, parameterList = copy.deepcopy(parameterList))

			# no [ ( [ listExpr {, listExpr} ] ) ]
			else:
				expr = AST.Variable(name = v_id)

		# (
		elif self.token.symbol() == 'leftparen':
			self.getToken()

			# expr -- store expr in expr
			expr = self.expr()

			# )
			if self.token.symbol() != 'rightparen':
				ErrorMessage('{0} expected'.format(')'), self.lexer.position(), self.lexer.echo())					

			self.getToken()

		# literal -- store literal in expr
		else:
			expr = self.literal()

		return expr

	# literal() : input: None, output: instance of appropriate AST object
	# Recognizes the following BNF where symbols preceded with underscores are in-language symbols	
	# literal ::= integer | Nil
	def literal(self):
		val = None

		# integer
		if self.token.symbol() == 'integer':
			val = AST.IntValue(value = self.token.lexeme())
			self.getToken()				

		# Nil -- a list
		elif self.token.symbol() == 'nil':
			val = AST.NilValue()
			self.getToken()

		return val		

def main(file):
	lexer = MicroTree(_input=file)
	print(repr(lexer.tree))

if __name__ == '__main__':
	main(file='Test3.scala')
