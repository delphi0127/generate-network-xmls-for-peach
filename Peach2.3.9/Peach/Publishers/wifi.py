
'''
AirPcap publisher for wifi fuzzing.

@author: Michael Eddington
@version: $Id$
'''

#
# Copyright (c) Michael Eddington
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

# $Id$

import sys, os, threading, time
from Peach.publisher import *

try:
	from ctypes import *
	
	class pcap_pkthdr(Structure):
		'''
		struct pcap_pkthdr {
			struct timeval ts;	/* time stamp */
			bpf_u_int32 caplen;	/* length of portion present */
			bpf_u_int32 len;	/* length this packet (off wire) */
		};
		'''
		_fields_ = [
			('ts', c_uint64),
			('caplen', c_uint),
			('len', c_uint)
			]
	
except:
	pass

class Wifi(Publisher):
	'''
	AirPcap I/O inteface.  Supports sending beacons and standard I/O.
	'''
	
	PCAP_ERRBUF_SIZE = 256
	AIRPCAP_LT_802_11 = 1				# plain 802.11 link type. Every packet in the buffer contains the raw 802.11 frame, including MAC FCS.
	AIRPCAP_LT_802_11_PLUS_RADIO = 2	# 802.11 plus radiotap link type. Every packet in the buffer contains a radiotap header followed by the 802.11 frame. MAC FCS is included.
	AIRPCAP_LT_UNKNOWN = 3				# Unknown link type. You should see it only in case of error.
	AIRPCAP_LT_802_11_PLUS_PPI = 4		# 802.11 plus PPI header link type. Every packet in the buffer contains a PPI header followed by the 802.11 frame. MAC FCS is included.
	
	def __init__(self, channel = 5, mac = "\xca\xce\xca\xce\xca\xce", device = "\\\\.\\airpcap00"):
		Publisher.__init__(self)
		self.mac = mac
		self.device = device
		self.channel = channel
		self.pcap = None
		self.air = None
		self.beacon = None
		self.beaconThread = None
		self.beaconStopEvent = None
		self.probe = None
		self.association = None
		
		# Don't initalize here to avoid a deepcopy
		# issue!
		#self.beaconStopEvent = threading.Event()
		#self.beaconStopEvent.clear()
	
	def start(self):
		
		if self.beaconStopEvent == None:
			self.beaconStopEvent = threading.Event()
		
		errbuff = c_char_p("A"*self.PCAP_ERRBUF_SIZE) # Must pre-alloc memory for error message
		self.pcap = cdll.wpcap.pcap_open_live(self.device, 65536, 1, 1000, errbuff)
		
		if self.pcap == 0:
			raise Exception( errbuff.value )
		
		self.air = cdll.wpcap.pcap_get_airpcap_handle(self.pcap)
		cdll.airpcap.AirpcapSetDeviceChannel(self.air, self.channel)
		cdll.airpcap.AirpcapSetLinkType(self.air, self.AIRPCAP_LT_802_11)
		self.beaconStopEvent.clear()
	
	def stop(self):
		if self.pcap != None:
			cdll.wpcap.pcap_close(self.pcap)
			self.pcap = None
		if self.beaconThread != None:
			self.beaconStopEvent.set()
			self.beaconThread.join()
			self.beaconThread = None
			self.beaconStopEvent.clear()
			self.beacon = None
	
	def send(self, data):
		cdll.wpcap.pcap_sendpacket(self.pcap, data, len(data))
	
	def receive(self, size = None):
		'''
		Receive some data.
		
		@type	size: integer
		@param	size: Number of bytes to return
		@rtype: string
		@return: data received
		'''
		
		cdll.wpcap.pcap_next_ex.argtypes = [
			c_void_p,
			POINTER(POINTER(pcap_pkthdr)),
			POINTER(POINTER(c_ubyte))
			]
		
		header = pointer(pcap_pkthdr())
		header.len = 0
		header.caplen = 0
		pkt_data = POINTER(c_ubyte)()
		
		while True:
			res = cdll.wpcap.pcap_next_ex(self.pcap, byref(header), byref(pkt_data))
			if res < 0:
				# error reading packets
				error = cdll.wpcap.pcap_geterr(self.pcap)
				raise Exception(error)
			
			elif res == 0:
				# timeout hit
				continue
			
			# Convert byte array to binary string
			
			data = ""
			cnt = 0
			for b in pkt_data:
				if cnt >= header.contents.len:
					break
				cnt += 1
				data += chr(b)
			
			# Check mac destination, assumes we want broadcasts
			
			dest_mac = data[4:10]
			src_mac = data[10:16]
			
			if src_mac == self.mac:
				continue
			
			if not (dest_mac == '\xff\xff\xff\xff\xff\xff' or dest_mac == self.mac):
				continue
			
			#print ">> Pkt type: %2x" % ord(data[0])

			# Is probe request?
			if ord(data[0]) == 0x40 and self.probe != None:
				print ">> Sending probe %2x %2x %2x %2x" % (ord(self.probe[-4]), 
				                                            ord(self.probe[-2]), 
				                                            ord(self.probe[-3]), 
				                                            ord(self.probe[-1]))
				self.send(self.probe)
				continue
			
			# Is Association request?
			if ord(data[0]) == 0x00 and self.association != None:
				print ">> Sending association"
				self.send(self.association)
				break
			
			if hasattr(self, "publisherBuffer"):
				self.publisherBuffer.haveAllData = True
			
			#return data
	
	def _sendBeacon(self):
		while not self.beaconStopEvent.isSet():
			cdll.wpcap.pcap_sendpacket(self.pcap, self.beacon, len(self.beacon))
			time.sleep(0.1)
	
	def _startBeacon(self):
		if self.beacon == None:
			return
		if self.beaconThread != None:
			return
		
		self.beaconThread = threading.Thread(target=self._sendBeacon)
		self.beaconThread.start()
	
	def call(self, method, args):
		
		if method == 'beacon':
			self.beacon = args[0]
			self._startBeacon()
		elif method == 'probe':
			print ">> Setting probe"
			self.probe = args[0]
			self.hexPrint(self.probe)
		elif method == 'association':
			print ">> Setting association"
			self.association = args[0]
			self.hexPrint(self.association)
		
	
	def connect(self):
		'''
		Called to connect or open a connection/file.
		'''
		pass
		
	def close(self):
		'''
		Close current stream/connection.
		'''
		pass

# end
