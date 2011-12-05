########################################################################################
#Copyright (C) 2009 Quest Software, Inc.
#File:		logger.py
#Version:	1.0.0.10

############################################################
#
#	THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND,
#	EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
#	WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.
#
############################################################
import os
import logging, traceback
import logging.handlers

def CreateIfNeedLogFolder(fileName):	
	import os
	folderName = os.path.dirname(fileName)
	if len(folderName) > 0 and not os.path.exists(folderName):
		os.mkdir(folderName)

def getLoggingLevel(logfile):
	levelName = getLoggingOption(logfile, "logging.level")
	return logging._levelNames[levelName]
	
def getLoggingOption(logfile, option):
	from ConfigParser import RawConfigParser
	logfile_path = os.path.dirname(logfile)
	conf_path = os.path.join(logfile_path, 'logger.conf')
	conf = RawConfigParser()
	conf.read(conf_path)
	return conf.get("global", option)
		
def multiargs(fn):
	""" Allow logger to be used with more than one argument.
		All arguments are forcing to convert to strings. 
		Used only with class functions!
		
		>>> class A():
		... 	@multiargs
		... 	def a( self, one ):
		... 		print one
		>>> A().a( 1 )
		1
		>>> A().a( '1', 2, 3 )
		1, 2, 3
	"""
	def patch(self, *args):
		mess = ", ".join( map( lambda x: "%s" % x, args ) )
		return fn(self, mess)
	return patch

class Log:
	"""
		Global LOG class to use in whole project.
		Examples:
		
		>>> # Preparation
		>>> import tempfile, re, os
		>>> fid, filename = tempfile.mkstemp()
		>>> def check_string_contains(str, filename):
		...		f = open(filename, 'rt')
		...		is_contains = re.search( str, f.read(), re.IGNORECASE )
		...		f.close()
		...		if is_contains: return True
		...		return False
		
		>>> # Creating instance
		>>> log = Log()
		>>> log.Init(filename)
		
		>>> # Tests
		>>> log.Info( 'Test info string' )
		>>> check_string_contains( 'Test info string', filename )
		True
		
		>>> check_string_contains( 'Test info absent string', filename )
		False
		
		>>> log.Info( 'This is INFO' )
		>>> check_string_contains( '\*\* INFO \*\* This is INFO', filename )
		True
		
		>>> log.Debug( 'This is DEBUG' )
		>>> check_string_contains( '\*\* DEBUG \*\* This is DEBUG', filename )
		True
		
		>>> log.Except( Exception('This is EXCEPT') )
		>>> check_string_contains( '\*\* ERROR \*\* This is EXCEPT', filename )
		True
		
		>>> log.Info( 'multi', 'value', 'logging:', 1, ['one', 1], {'key': 'value'} )
		>>> check_string_contains( "\*\* INFO \*\* multi, value, logging:, 1, \['one', 1\], \{'key': 'value'\}", filename )
		True
		
		>>> log.Traceback( 'Traceback' )
		>>> check_string_contains( "\*\* DEBUG \*\* Traceback", filename)
		True
		>>> check_string_contains( 'File "logger\.py", line \d+, in Traceback\', filename )
		True
		>>> check_string_contains( 'self\.Debug\(.*join\(\s*traceback\.format_stack', filename)
		True
		
		>>> # Cleaning
		>>> os.remove( filename )
	"""
	_log = logging.getLogger()

	def Init(self, filename):
		CreateIfNeedLogFolder(filename)
		self._log.setLevel(getLoggingLevel(filename))
		formatter = logging.Formatter("%(asctime)s [%(process)d:%(thread)d] ** %(levelname)s ** %(message)s")
		maxBytes = getLoggingOption(filename, "logging.maxbytes")
		handler = logging.handlers.RotatingFileHandler(filename, maxBytes=int(maxBytes), backupCount=1)
		handler.setFormatter(formatter)
		self._log.addHandler(handler)
	
	@multiargs
	def Info(self, mess):
		self._log.info(mess)
	info = Info

	@multiargs
	def Debug(self, mess):
		self._log.debug(mess)
	debug = Debug
	
	@multiargs
	def Except(self, mess):
		self._log.exception(mess)

	@multiargs
	def Error(self, mess):
		self._log.error(mess)		
		
	
	@multiargs
	def Traceback(self, mess):
		""" Write message to log and it's traceback. """
		self.Debug( mess )
		self.Debug( "\n" + "".join( traceback.format_stack() ) )
		
	traceback = Traceback

log = Log()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
