'''
Base classes for strategy implementations.
'''


from Engine.common import *

class StrategyError(PeachException):
	pass

class RouteDescriptor:
	'''
	Used to describe the route.
	'''
	
	def __init__(self):
		self.paths = []
		self.index = 0
	
	'''
	Add a stop that resultant route must pass over 
	'''
	def addPath(self, path):
		if path == None:
			raise PeachException("Argument::path cannot be None!")
		
		self.paths.append(path)
	
	def reset(self):
		self.index = 0
		
	def clear(self):
		del self.paths[:]
	
	
	'''
	This method is handy when there is no pair but only a path
	'''
	def hasNextSingle(self):
		return (len(self.paths) == 1) and (self.index < len(self.paths))
	
	'''
	To get the current path
	'''	
	def nextSingle(self):
		if not self.hasNextSingle():
			raise PeachException("End of the route description is reached!")
		
		self.index += 1
		return self.paths[self.index - 1]
	
	'''
	Returns True when it has two paths more to visit 
	otherwise False  
	'''
	def hasNextPair(self):
		return (self.index < len(self.paths) - 1) 
	
	'''
	Returns the next pair which strategy will find a proper path in between.
	If hasNextPair() returns False then this method completes the pair to be returned
	with a None and yields the result.
	'''
	def nextPair(self):
		if not self.hasNextPair():
			raise PeachException("End of the route-pairs is reached!")
		
		self.index += 1
		return [self.paths[self.index - 1], self.paths[self.index]]
		
class Strategy:
	'''
	Strategy is an abstract class that is used to define a method 
	to find out a route	between start and destination paths. 
	'''
	def __init__(self, stateMachine, routeDescriptor, params = None):
		
		self.params = {}
		if params != None:
			self.params = params
		
		if routeDescriptor == None:
			raise PeachException("Argument::routeDescriptor cannot be None!")
		
		self.routeDesc = routeDescriptor
		self.stateMachine = stateMachine 
		
	'''
	This method invokes abstract _findRoute method for each pair taken from routeDescriptor 
	to obtain a proper route and finally returns the route.
	'''	
	def getRoute(self):
		route = []
		while self.routeDesc.hasNextPair():
			[start, destination] = self.routeDesc.nextPair()
			partialRoute = self._findRoute(start, destination)
			if len(route) == 0:
				route.extend(partialRoute)
			else:
				#skip the first path as we already have it ;)
				route.extend(partialRoute[1:])
		
		if self.routeDesc.hasNextSingle():
			lastPath = self.routeDesc.nextSingle()
			route.extend(self._findRoute(lastPath, None))
		
		return route
	
	'''
	This method is used to explore a route(list of paths) in between
	start and destination paths.
	
	@param start: start path
	@param destination: destination path
	@return: a list of paths starting with parameter start and 
			ending with parameter destination.
	'''
	def _findRoute(self, start, destination):
		pass
	
	
	'''
	Used to reset a strategy especially when re-discovering the route.
	'''
	def _reset(self):
		self.routeDesc.reset()
		
class StrategyCollection(Strategy):
	'''
	This class behaves like a proxy between strategies
	defined in XML file, which is used to run all the strategies
	respectively to produce a resultant route.
	'''
	def __init__(self):
		Strategy.__init__(self, None, RouteDescriptor())
		self.strategies = []
		self.route = None
		
	def addStrategy(self, strategy):
		self.strategies.append(strategy)
		#re-explore the route as we have a new strategy
		self._reset()
		
	def getRoute(self):
		if self.route != None:
			return self.route
		
		self.route = []
		for strategy in self.strategies:
			self.route.extend(strategy.getRoute())
		
		return self.route 
	
	def _reset(self):
		self.route = None
		for strategy in self.strategies:
			strategy._reset()
			
			
from Strategies import *
class StrategyFactory:
	'''
	To centralize the creation of strategies
	'''
	
	def __init__(self, defStrategy = "default.StaticStrategy"):
		self.defStrategy = defStrategy
	
	def createStrategy(self, stateMachine, routeDescriptor, clazz = None,  params = None):
		if clazz == None:
			clazz = self.defStrategy
			
		try:
			code = clazz + "(stateMachine, routeDescriptor, params)"
			print "StrategyFactory::createStrategy: ", code
			strategy = eval(code)
			
			if strategy == None:
				raise PeachException("StrategyFactory::createStrategy: Unable to create Strategy [%s]" % clazz)
			
			return strategy
		except:
			raise PeachException("StrategyFactory::createStrategy: Unable to create Strategy [%s]" % clazz)
		