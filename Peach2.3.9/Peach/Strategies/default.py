
from Peach.strategy import *

class StaticStrategy(Strategy):
	
	def __init__(self, stateMachine, routeDescriptor, params = None):
		Strategy.__init__(self, stateMachine, routeDescriptor)
		
	def _findRoute(self, start, destination):
		if destination == None:
			return [start]
		
		return [start, destination]

		
	