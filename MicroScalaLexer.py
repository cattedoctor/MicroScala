# MicroScala Lexical analyzer implementation
# MicroScalaLexer is a class to represent a tokenizer and lexer
# for the MicroScala programming language. It accepts an Scala file as
# input and tokenizes it with MicroScalaLexer and Token classes,
# returning errors and halting execution when appropriate.
# Author : Jo
# License : Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)

#!/usr/bin/env python

from optparse import OptionParser
import os, logging, sys
import math, re, collections
from ErrorMessage import ErrorMessage
from Token import Token

# tokens is an OrderedDictionary where entry is preserved
# -- e.g. first key, val pair input into the dictionary is
# the first pair checked every time; similarly, last is last.
tokens = collections.OrderedDict()
tokens['comment']     = re.compile(r'^\/\/.*')
tokens['semicolon']   = re.compile(r'^;')
tokens['cons']        = re.compile(r'^::')
tokens['colon']       = re.compile(r'^:')
tokens['period']      = re.compile(r'^\.')
tokens['comma']       = re.compile(r'^,')
tokens['leftbrace']   = re.compile(r'^\{')
tokens['rightbrace']  = re.compile(r'^\}')
tokens['leftbracket'] = re.compile(r'^\[')
tokens['rightbracket']= re.compile(r'^\]')
tokens['or']    	  = re.compile(r'^\|\|')
tokens['and']         = re.compile(r'^&&')
tokens['relop'] 	  = re.compile(r'^(<=|<|>=|>|==|!=)')
tokens['not']         = re.compile(r'^!')
tokens['leftparen']   = re.compile(r'^\(')
tokens['rightparen']  = re.compile(r'^\)')
tokens['addop'] 	  = re.compile(r'^(\+|\-)')
tokens['multop']      = re.compile(r'^(\*|\/)')
tokens['assign']      = re.compile(r'^=')
tokens['args']        = re.compile(r'^args')
tokens['array']	      = re.compile(r'^Array')
tokens['def']   	  = re.compile(r'^def')
tokens['else']  	  = re.compile(r'^else')
tokens['listop']      = re.compile(r'^(head|isEmpty|tail)')
tokens['if']    	  = re.compile(r'^if')
tokens['int']   	  = re.compile(r'^Int')
tokens['list']  	  = re.compile(r'^List')
tokens['main']  	  = re.compile(r'^main')
tokens['nil']   	  = re.compile(r'^Nil')
tokens['object']	  = re.compile(r'^object')
tokens['println']     = re.compile(r'^println')
tokens['return']	  = re.compile(r'^return')
tokens['string']	  = re.compile(r'^String')
tokens['var'] 	      = re.compile(r'^var')
tokens['while'] 	  = re.compile(r'^while')
tokens['identifier']  = re.compile(r'^[a-zA-Z](_?[a-zA-Z0-9]+)*')
tokens['integer']     = re.compile(r'^[0-9]+')
tokens['space']	      = re.compile(r'^[ \t\n]+')
tokens['e']           = re.compile(r'')

class MicroScalaLexer(object):
	def __init__(self, _input):
		self.__position = 0
		self.__text = []
		self.__len = 0
		self.__tokens = []
		self.__line = ''
		self.__leading_space = ''

		# parse input file into array broken up by line
		with open(_input, 'r') as f:
			self.__text = f.read().split('\n')

		self.__len = len(self.__text)

	# print the current line and remaining text of that line
	def echo(self):
		print(self.__line, self.__text[0])

	# return current position of lexer as an integer
	def position(self):
		return int(self.__position)

	# return a list of tokens as (symbol, lexeme), one per line
	def token_list(self):
		for token in self.__tokens:
			print(repr(token))

	# return true if more tokens remain, false if input file is fully parsed
	def tokens_remain(self):
		if self.__len != 0:
			return True
		else:
			return False

	# bookkeeping of the line to allow pretty printing
	def __update_line(self, string):
		self.__position += len(string)
		self.__line += ' ' + string

		# remove the leading captured lexeme from current input line
		self.__text[0] = re.sub('^{0}'.format(re.escape(string)), '', self.__text[0])
		
		# if current line has no more tokens to parse
		if (self.__text[0] == '') or (self.__text[0] == '\n') or (self.__text[0] == ' '):
			# remove the line from remaining text array
			self.__text.pop(0)

			# reset the lexer line position
			self.__position = 0

			# print the fully parsed input line
			print('{0}{1}'.format(self.__leading_space, self.__line))

			# reset the text holder
			self.__line = ''

			# update the line length
			self.__len = len(self.__text)

		tmp = None
		# if the length is not zero
		if self.__len > 0:
			# match the leading spaces
			tmp = re.match(r'^\s+', self.__text[0])

			# before stripping them from the text line
			self.__text[0] = self.__text[0].lstrip()

		# if leading spaces exist
		if tmp != None:
			# capture them
			self.__leading_space = tmp.group(0)
		else:
			self.__leading_space = ''
				
	# get the next token
	def nextToken(self):
		# if length is non-zero of current line
		if self.__len > 0:
			# iterate through OrderedDict of tokens (where order is preserved)
			for k, v in tokens.items():
				# if the regex value matches the beginning of the line
				if v.match(self.__text[0]):
					# capture it into string
					string = v.match(self.__text[0]).group(0)

					# if the key is not epsilon
					if k != 'e':
						# append a new token pair (symbol = k, lexeme = string)
						self.__tokens.append(Token(symbol=k, lexeme=string))

					# update line with captured lexeme
					self.__update_line(string)

					# return the token captured
					return Token(symbol=k, lexeme=string)

			# return an unknown token if not in token dictionary
			return Token(symbol='UNK', lexeme=None)

		# return an EOF token when end-of-file has been reached
		else:
			return Token(symbol='EOF', lexeme='EOF')

# Runs the program when called by itself from command-line
def main(file):
	# Create an instance of MicroSclaLexer class with given input file
	lexer = MicroScalaLexer(_input=file)

	# Iterate through the input file until all tokens have been parsed
	while lexer.tokens_remain() is True:
		lexer.nextToken()

	# Print list of tokens
	lexer.token_list()

if __name__ == '__main__':
	main(file='Test3.scala')
