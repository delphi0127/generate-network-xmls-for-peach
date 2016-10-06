
from Peach.strategy import *

	
class RandomStrategy(Strategy):
	
	def __init__(self, stateMachine, routeDescriptor, params = None):
		Strategy.__init__(self, stateMachine, routeDescriptor, params)
	
	def _findRoute(self, start, destination):
		'''
		Will be implemented soon 
		'''
		print int(self.params['maxsteps'])
		
		return [start, destination]

# end
