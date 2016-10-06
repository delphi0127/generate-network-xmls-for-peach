'''
An embeded web server that displays fuzzing status.

@authors: Michael Eddington (mike@phed.org)
		  Blake Frantz (blakefrantz@gmail.org)

@version: $Id: webwatcher.py 863 2008-05-11 10:25:32Z meddingt $
'''

#
# Copyright (c) 2007-2008 Michael Eddington
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
#	Blake Frantz(blakefrantz@gmail.com)
#
# $Id: webwatcher.py 863 2008-05-11 10:25:32Z meddingt $


import sys, os, time, threading
from parser import *
from dom import DomPrint
from engine import *
import engine

from twisted.web import server, resource, static
from twisted.internet import reactor

class WebHandler(resource.Resource):

	gadgetData = "%RUN_NAME%,%TEST_NAME%,%TEST_COUNT%,%TEST_TOTALCOUNT%,%FAULT_COUNT%"

	html = """

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=iso-8859-1"/>
<meta http-equiv="refresh" content="10" />
<title>Peach Run Monitor</title>
<style>
/*#############################################################
Name: Indigo
Description: A lightweight (7kb images), simple and professional design.
Date: 2006-07-27
Author: Viktor Persson
URL: http://arcsin.se

Feel free to use and modify but please provide credits.
#############################################################*/

/* standard elements */
* {
	margin: 0;
	padding: 0;
}
a {
	color: #F70;
}
a:hover {
	color: #C60;
}
body {
	background: #0094D6 url(img/bg.gif) repeat-x;
	color: #466;
	font: normal 62.5% "Lucida Sans Unicode",sans-serif;
	margin: 0;
}
input {
	color: #555;
	font: normal 1.1em "Lucida Sans Unicode",sans-serif;
}
p,cite,code,ul {
	font-size: 1.2em;
	padding-bottom: 1.2em;
}
h1 {
	font-size: 1.4em;
	margin-bottom: 4px;
}
code {
	background: url(img/bgcode.gif);
	border: 1px solid #F0F0F0;
	border-left: 6px solid #39F;
	color: #555;
	display: block;
	font: normal 1.1em "Lucida Sans Unicode",serif;
	margin-bottom: 12px;
	padding: 8px 10px;
	white-space: pre;
}
cite {
	background: url(img/quote.gif) no-repeat;
	color: #666;
	display: block;
	font: normal 1.3em "Lucida Sans Unicode",serif;
	padding-left: 28px;
}
h1,h2,h3 {
	color: #06C;
	padding-top: 6px;
}
/* misc */
.clearer {
	clear: both;
}

/* structure */
.container {
	background: url(img/topleft.png) no-repeat;
}

.header {
	height: 92px;
}

/* title */
.title {
	float: left;
	padding: 28px 0 0 76px;
}
.title h1 {
	color: #FFF;
	font: normal 2em Verdana,sans-serif;
}
/* navigation */
.navigation {
	float: left;
	height: 92px;
	margin-left: 24px;
	padding: 0 16px;
}
.navigation a {
	color: #FFF;
	float: left;
	font: bold 1.2em "Trebuchet MS",sans-serif;
	margin-top: 56px;
	padding: 8px 18px;
	text-align: center;
	text-decoration: none;
}
.navigation a:hover {
	background-color: #4A91C3;
	color: #FFF;
}

/* main */
.main {
	background: #FFF url(img/bgmain.gif) no-repeat;
	clear: both;
	padding: 12px 12px 0 52px;
}

/* main left */
.sidenav {
	float: left;
	width: 24%;
}
.sidenav h1 {
	border-bottom: 1px dashed #DDD;
	color: #E73;
	font-size: 1.2em;
	height: 20px;
	margin-top: 1.2em;
}
.sidenav ul {
	margin: 0;
	padding: 0;
}
.sidenav li { 
	border-bottom: 1px dashed #EEE;
	list-style: none;
	margin: 0;
}
.sidenav li a {
	color: #777;
	display: block;
	font-size: 0.9em;
	padding: 3px 6px 3px 18px;
	text-decoration: none;
}
.sidenav li a:hover {
	color: #111;
	background: url(img/nav_li.gif) no-repeat;
}

/* content */
.content {
	float: left;
	margin-right: 4%;
	width: 69%;
}
.content .descr {
	color: #C60;
	margin-bottom: 6px;
}
.content li {
	list-style: url(img/li.gif);
	margin-left: 18px;
}

/* search form */
.styled {
	border: 3px double #E5E5E5;
	padding: 2px 3px;
}
.button {
	border: 1px solid #AAA;
	margin-left: 5px;
	padding: 2px 3px;
}

/* footer */
.footer {
	background: #0094D6 url(img/bgfooter.gif) repeat-x;
	color: #C1DEF0;
	font-size: 1.1em;
	line-height: 40px;
	text-align: center;
}
.footer a {
	color: #FFF;
	text-decoration: none;
}
.footer a:hover {
	color: #FFF;
	text-decoration: underline;
}
</style>
</head>
<body>
<div class="container">
	<div class="header">
		<div class="title">
			<h1>Peach Run Monitor</h1>
		</div>
	</div>
	<div class="main">
		<div class="content">
			<h1>%RUN_NAME% -- %TEST_NAME%</h1>
			<div class="descr">%TEST_COUNT% of %TEST_TOTALCOUNT% <b>/</b> %FAULT_COUNT% faults detected</div>
			<p></p>
			
			<b>Current test case:</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
			<!-- <b>Length</b>: %TEST_VALUE_LENGTH%<br /> -->
			%TEST_VALUE%

			<br /><br /><br /><br /><br /><br /><br />
			<br /><br /><br /><br /><br /><br /><br />
			<br /><br /><br /><br /><br /><br /><br />
			
			<br />
			<br />
			<p>
			</p>
		</div>
		<div class="sidenav">
			<br />
			%FAULTS%
<!--			<br />
			<p>
				Fault detected on test case #47<br />
				<ul>
					<li><a href="">Data.txt</a></li>
					<li><a href="">Debugger.txt</a></li>
					<li><a href="">Network.pcap</a></li>
				</ul>
			</p> -->
		</div>
		<div class="clearer"><span> </span></div>
	</div>
</div>
<div class="footer">&nbsp;</div>
</body>
</html>"""
	
	isLeaf = True
	
	#def getChild(self, name, request):
	#	if name == '':
	#		return self
	#	
	#	return Resource.getChild(self, name, request)
	
	ret = ""
	
	dataUri = re.compile(r"^/stuff/(\d+)_(\d+)_(.*)$")
	
	#vista gadget uri
	gadgetDataUri = re.compile(r"^/\?gadgetData")
	
	def render_GET(self, request):
	
		self.parent._lock.acquire()
		
		try:
			
			#print repr(request)
			#print "Uri: " + request.uri
			m = self.dataUri.search(request.uri)
			if m != None:
				# feed back our run data
				faultIndex = int(m.group(1))
				faultKey = m.group(3)
				
				if faultKey[-3:] == "txt":
					return "<body><pre>" + self.parent._faultData[faultIndex][1][faultKey] + "</pre></body>"
				
				else:
					ret = self.parent._faultData[faultIndex][1][faultKey]
				
				self.parent._lock.release()
				return ret
			
			# support for Vista Gadget
			m = self.gadgetDataUri.search(request.uri)			
			
			if m != None:
				ret = self.gadgetData
			else:
				ret = self.html
			
			# swap in values
			if self.parent._run != None:
				ret = ret.replace("%RUN_NAME%", self.parent._run.name)
			else:
				ret = ret.replace("%RUN_NAME%", "")
			if self.parent._test != None:
				ret = ret.replace("%TEST_NAME%", self.parent._test.name)
			else:
				ret = ret.replace("%TEST_NAME%", "")
			if self.parent._variationCount != None:
				ret = ret.replace("%TEST_COUNT%", str(self.parent._variationCount))
			else:
				ret = ret.replace("%TEST_COUNT%", "")
			if self.parent._totalVariations!= None:
				ret = ret.replace("%TEST_TOTALCOUNT%", str(self.parent._totalVariations))
			else:
				ret = ret.replace("%TEST_TOTALCOUNT%", "")
			if self.parent._value != None:
				
				buff = ""
				for value in self.parent._value:
					if len(value) < 3:
						continue
					
					buff += "<b>%s: %s&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;length: %d</b><br/><textarea rows=\"20\" cols=\"60\" readonly=\"true\">%s</textarea><br/>" % (value[1], value[0], len(value[2]), repr(value[2]))
					
				ret = ret.replace("%TEST_VALUE%", buff)
			else:
				ret = ret.replace("%TEST_VALUE%", "")
			
			ret = ret.replace("%FAULT_COUNT%", str(self.parent._faultCount))
			
			faultHtml = ''
			if self.parent._faultCount > 0:
				# build a fault block
				
				for i in range(len(self.parent._faultData)):
					fault = self.parent._faultData[i]
					
					faultHtml += '<br /><p>Fault detected on test case #' + str(fault[0]) + '<br /><ul>'
					
					for key in fault[1].keys():
						faultHtml += '<li><a href="/stuff/%d_%d_%s">%s</a></li>' % (i, fault[0], key, key)
					
					faultHtml += '</ul></p>'
				
			ret = ret.replace("%FAULTS%", faultHtml)
		
		finally:
			self.parent._lock.release()
		
		return str(ret)

class PeachWebWatcher(threading.Thread):
	'''
	Base for a class that receives callback when events occur
	in the Peach Engine.
	'''
	
	def __init__(self, port = 9001):
		threading.Thread.__init__(self)
		
		self._port = port
		self._run = None
		self._test = None
		self._totalVariations = 0
		self._variationCount = 0
		self._value = None
		self._exception = None
		self._isFinished = False
		self._lock = threading.Lock()
		self._faultCount = 0
		self._faultData = []
		
		self.start()
		
		# This will never work on Liunx/OS X :)
		try:
			params = [ 'explorer', "http://127.0.0.1:"+str(self._port)]
			ret = os.spawnv(os.P_NOWAIT, "c:/windows/explorer.exe", params )
		except:
			pass
	
	def run(self):
		if engine.__file__[1] != ':':
			imgPath = os.path.dirname(os.path.join(os.getcwd(), engine.__file__))
		else:
			imgPath = os.path.dirname(engine.__file__)
		imgPath = os.path.join(imgPath, 'img')
		
		res = static.File(imgPath)
		handler = WebHandler()
		
		res.putChild('img', static.File(imgPath))
		res.putChild('', handler)
		res.putChild('stuff', handler)
		
		#self._site = server.Site(handler)
		self._site = server.Site(res)
		handler.parent = self
		reactor.listenTCP(9001, self._site)
		print "Listening on port 9001."
		reactor.run(installSignalHandlers=0)
	
	def setTotalVariations(self, totalVariations):
		self._lock.acquire()
		self._totalVariations = totalVariations
		self._lock.release()
		
	def OnRunStarting(self, run):
		self._lock.acquire()
		self._run = run
		self._lock.release()
	
	def OnRunFinished(self, run):
		self._lock.acquire()
		self._isFinished = True
		self._lock.release()
		
		print "\n\n --- Type CTRL-BREAK To End Peach Web Server --- \n"
	
	def OnTestStarting(self, run, test, totalVariations):
		self._lock.acquire()
		self._test = test
		self._totalVariations = totalVariations
		self._lock.release()
	
	def OnTestFinished(self, run, test):
		self._lock.acquire()
		self._test = None
		self._lock.release()

	def OnTestCaseStarting(self, run, test, variationCount):
		pass
	
	def OnTestCaseReceived(self, run, test, variationCount, value):
		pass
	
	def OnTestCaseException(self, run, test, variationCount, exception):
		self._lock.acquire()
		self._exception = exception
		self._lock.release()
	
	def OnTestCaseFinished(self, run, test, variationCount, actionValues):
		self._lock.acquire()
		self._variationCount = variationCount
		self._value = actionValues
		self._lock.release()

	def OnFault(self, run, test, variationCount, monitorData, value):
		self._faultCount += 1
		self._faultData.append((variationCount, monitorData))


# end
