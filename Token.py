# Token.py : Implements a Token class that stores a symbol and lexeme for a token
# Author : Jo
# License : Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)

# UNDEFINED holds the value of an undefined integer

UNDEFINED = -32768

class Token(object):
	def __init__(self, symbol, lexeme=None):
		self.__symbol = str(symbol)
		self.__lexeme = str(lexeme)

	def symbol(self):
		return self.__symbol

	def lexeme(self):
		return self.__lexeme

	def __repr__(self):
		return "({0}, {1})".format(self.__symbol, self.__lexeme)
