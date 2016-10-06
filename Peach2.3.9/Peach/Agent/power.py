
'''
Monitors to control networked power strips.

@author: Michael Eddington
@author: Adam Cecchetti
@version: $Id: power.py 1324 2008-10-23 06:12:53Z meddingt $
'''

#
# Copyright (c) 2007 Michael Eddington
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in	
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

# Authors:
#   Michael Eddington (mike@phed.org)
#	Adam Cecchetti

# $Id: power.py 1324 2008-10-23 06:12:53Z meddingt $


import sys, threading, os, time, thread, re, socket
import urllib, urllib2, cookielib
import hashlib, time  

from Peach.agent import Monitor

class _PowerControl:
	'''Class to control IP9258 ip power strip.
	'''

	uri = ""
	loginurl = "/tgi/login.tgi"
	powerurl = "/tgi/iocontrol.tgi"
	username = ""
	password = "" 

	req_headers = { 
		'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
		'Referer':'',
	}

	def __init__( self, uri, username, password ):
		self.uri = uri
		self.username = username
		self.password = password
		self.data = []
		cookiejar = cookielib.CookieJar()
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))	
		urllib2.install_opener(opener)


	def login( self ):
		url = self.uri 
		req = urllib2.Request( url, None, self.req_headers )
		response = urllib2.urlopen( req )
		data = response.read()
		p = re.compile( 'NAME=\"Challenge\" VALUE=\"(.*)\"> <input' )	
		m = p.search( data )
		challenge = m.group(1)

		md5hex = hashlib.md5()
		md5hex.update( self.username + self.password + challenge )
		md5response = md5hex.hexdigest()

		self.password=""

		login_data = { 
			'Username': self.username, 
			'Response':  md5response,
			'Challenge': '',
			'Password': ''
		}
			
		urldata = urllib.urlencode( login_data )
		req = urllib2.Request( self.uri + self.loginurl, urldata, self.req_headers )
		response = urllib2.urlopen( req )
		data = response.read()
		

	def powerAllOn(self):
		return "Not impl"

	def powerAllOff(self):
		return "Not impl" 

	def powerOn(self, machine):
		self.powerchange(machine, "On")

	def powerOff(self, machine): 
		self.powerchange(machine, "Off") 

	def powerchange(self, machine_id, state):

		if(machine_id < 1 or  machine_id > 4):
			print "Invalid Machine ID" 
			return 

		if(state != "On" and state != "Off"):
			print "Invalid State"
			return 
		
		req = urllib2.Request( self.uri + self.powerurl, None, self.req_headers )
		response = urllib2.urlopen( req ) 
		data = response.read()
		
		P = ["Off", "Off", "Off", "Off"]

		#fuggly TODO:clean me up later  
		p= re.compile('NAME="P60" VALUE="On" CHECKED>')
		if( p.search( data ) != None):
			P[0]="On"
		else:
			P[0]="0ff" 

		p= re.compile('NAME="P61" VALUE="On" CHECKED>')
		if( p.search( data ) != None):
			P[1]="On"
		else:
			P[1]="0ff" 

		p= re.compile('NAME="P62" VALUE="On" CHECKED>')
		if( p.search( data ) != None):
			P[2]="On"
		else:
			P[2]="0ff" 
			
		p= re.compile('NAME="P63" VALUE="On" CHECKED>')
		if( p.search( data ) != None):
			P[3]="On"
		else:
			P[3]="0ff" 

		P[machine_id-1] = state 
		
		urldata="P60=" + P[0] + "&P60_TS=0&P60_TC=Off&P61=" + P[1] + "&P61_TS=0&P61_TC=Off&P62=" + P[2] + "&P62_TS=0&P62_TC=Off&P63=" + P[3] + "&P63_TS=0&P63_TC=Off&ButtonName=Apply"
		#print urldata
		req = urllib2.Request( self.uri + self.powerurl, urldata, self.req_headers )
		response = urllib2.urlopen( req )

	def powercycle(self, machine): 
		self.powerOff(machine)
		time.sleep(5)
		self.powerOn( machine )

class NetworkedPower(Monitor):
	'''
	Monitor that will cycle the power port of a networked
	power strip.  Usefull for rebooting a machine after
	a fault is detected, or every N tests.
	
	Currently only works with "IP9258".
	'''
	
	def __init__(self, args):
		'''
		Constructor.  Arguments are supplied via the Peach XML
		file.
		
		@type	args: Dictionary
		@param	args: Dictionary of parameters
		'''
		
		self.hostname = str(args['hostname'])
		self.username = str(args['username'])
		self.password = str(args['password'])
		self.port = int(args['port'])
		self.waitTime = int(args['waittime'])
		
		# Cycle power every N tests.
		try:
			self.testCount = int(args['testcount'])
		except:
			self.testCount = None
		
		self.count = 0
		
		# Our name for this monitor
		self._name = "NetworkedPower"
	
	def OnTestStarting(self):
		'''
		Called right before start of test case or variation
		'''
		if self.testCount != None and self.testCount == self.count:
			self.count = 0
			pc = _PowerControl("http://" + self.hostname, self.username, self.password)
			pc.login()
			pc.powercycle(self.port)
			time.sleep(self.waitTime)
		
		else:
			self.count += 1
	
	def OnFault(self):
		'''
		Called when a fault was detected.
		'''
		pc = _PowerControl("http://" + self.hostname, self.username, self.password)
		pc.login()
		pc.powercycle(self.port)
		pc.powerOn(self.port)
		
		time.sleep(self.waitTime)


class AMTPower(Monitor):
	'''
	The tragety that is controling our AMT boxen!
	'''
		
	def __init__(self, args):
		'''
		Constructor.  Arguments are supplied via the Peach XML
		file.
		
		@type	args: Dictionary
		@param	args: Dictionary of parameters
		'''
		
		self.targethostname = str(args['targethostname'])
		self.makehostname = str(args['makehostname'])
		self.makeport = int(args['makeport'])
		self.hostname = str(args['hostname'])
		self.username = str(args['username'])
		self.password = str(args['password'])
		self.port = int(args['port'])
		self.waitTime = int(args['waittime'])
		
		# Cycle power every N tests.
		try:
			self.testCount = int(args['testcount'])
		except:
			self.testCount = None
		
		self.count = 0
		
		# Our name for this monitor
		self._name = "NetworkedPower"
	
	def _canWePing(self):
		pipe = os.popen("ping -n 2 " + self.targethostname)
		buff = pipe.read()
		pipe.close()
		
		if re.compile(r"Reply from \d+\.\d+\.\d+\.\d+: bytes=", re.M).search(buff) != None:
			return True
		
		return False
	
	def _powerCycle(self):
		pc = _PowerControl("http://" + self.hostname, self.username, self.password)
		pc.login()
		pc.powercycle(self.port)
	
	def _hitDahButton(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((self.makehostname, self.makeport))
		s.send('O')
		s.close()
	
	def OnTestStarting(self):
		'''
		Called right before start of test case or variation
		'''
		if self.testCount != None and self.testCount == self.count:
			self.count = 0
			
			self._powerCycle()
			self._hitDahButton()
			
			while not self._canWePing():
				time.sleep(1)
		
		else:
			self.count += 1
	
	def OnFault(self):
		'''
		Called when a fault was detected.
		'''
		pc = _PowerControl("http://" + self.hostname, self.username, self.password)
		pc.login()
		pc.powercycle(self.port)
		pc.powerOn(self.port)
		
		time.sleep(self.waitTime)
	

# end
