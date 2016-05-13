# ErrorMessage.py : ErrorMessage class for use in the micro Scala project
# This file contains all classes necessary to build an AST for the MicroScala language.
# Author : Jo
# License : Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)

import sys

class ErrorMessage(object):
	def __init__(self, message, position=None, echo=None):
		if position == None:
			print('***** Error {0} *****'.format(message))
		else:
			if echo != None:
				print(echo)
			print("{0}^\n{1} at pos={2}".format(" "*position, message, position))

		sys.exit(0)
