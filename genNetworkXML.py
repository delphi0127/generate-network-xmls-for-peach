#!/usr/bin/python
#-*- coding: utf-8 -*-
#author:delphi0127
#email:delphi0127@163.com
#generate every XML by every packet


import argparse, sys, socket, logging
from array import *
from random import choice
from time import sleep

#ipv6 warnings..
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

try: from scapy.all import *
except: from scapy import *

from scapy.utils import rdpcap, wrpcap
from scapy.layers.inet import IP,UDP,TCP
from scapy.packet import Raw


#this need to change for every target application
target_name = "amule"
pcapfile = "c:\\test\\amule1.pcap"
commandline_str ="""			<Param name="CommandLine" value="C:\\Program Files\aMule\\amule.exe"/> """



NAME          = "Generate XMLs for peach from pcap file."
VERSION       = "0.1"


XML_0 = """<?xml version="1.0" encoding="utf-8"?>
<Peach xmlns="http://phed.org/2008/Peach" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://phed.org/2008/Peach ../peach.xsd" version="1.0"
	author="Michael Eddington" description="Hello World Example">


	<Include ns="default" src="file:defaults.xml" />

	<DataModel name="HttpRequest">
"""

data_str =""" <String value="Hello World!" /> """     

XML_1 = """
	</DataModel>
	
	<StateModel name="TheStateModel" initialState="TheState">
		<State name="TheState">
			<Action type="output">
				<DataModel ref="HttpRequest" />
			</Action>
		</State>
	</StateModel>

	<!-- Agents that run localy will be started automatically by Peach -->
	<Agent name="LocalAgent">
		<Monitor name="Debugger" class="debugger.WindowsDebugEngine">
        """
#it should be customized for every xml.
#commandline_str ="""			<Param name="CommandLine" value="C:\Program Files\aMule\amule.exe"/> """
#"C:\Program Files\aMule\amule.exe"

XML_2 = """
		</Monitor>


	</Agent>

	<Test name="NetworkTest">
		<Agent ref="LocalAgent" />
		<StateModel ref="TheStateModel"/>

"""


publisher_str = """
		<Publisher class="tcp.Tcp">
			<Param name="host" value="127.0.0.1" />
			<Param name="port" value="4242" />
		</Publisher>

"""

XML_3 = """
	</Test>

	<Run name="DefaultRun">
		<Test ref="NetworkTest" />
"""


logger_str_win = """	
		<Logger class="logger.Filesystem">
			<Param name="path" value="c://test//logs" />
		</Logger>
"""

logger_str_unbuntu = """	
		<Logger class="logger.Filesystem">
			<Param name="path" value="/root/cloud/logs" />
		</Logger>
"""

XML_4 = """
	</Run>

</Peach>
<!-- end -->
 """

def getPayload(pcap_file):
    packets = rdpcap(pcap_file)
    
    for packet_content in packets:
        packet_list = []
        if packet_content.haslayer(TCP):
            for packet_payload in str(packet_content.getlayer(TCP).payload):
                print packet_payload #added by delphi0127                


        if packet_content.haslayer(UDP):
            for packet_payload in str(packet_content.getlayer(UDP).payload):
                print packet_payload #added by delphi0127





def genXMLs(pcap_file):
    global XML_0,data_str,XML_1,XML_2,publisher_str,XML_3,logger_str_win,logger_str_unbuntu,XML_4,target_name,pcapfile
    port = 1
    
    
    '''
    #1, wireshark filter rules
    cmd_filter="%s && ip.src==%s && ip.dst==%s && %s.srcport==%s && %s.port==%s"% \  
               (Node['proto'].lower(),Node['src'],Node['dst'],Node['proto'].lower(),Node['sport'],Node['proto'].lower(),Node['dport'])  
    
        
    os.system('start /WAIT "" "%s\tshark" -r "%s" -R "%s" -w "%s"'%(Wireshark_path,pcap_filename,cmd_filter,Temp_pcap_File))  
    '''

    Temp_pcap_File = "target.pcap"
    cmd_filter = "tcp.port==4662 or udp.port==4665 or udp.port==4672"
    Wireshark_path = "C:\Program Files\Wireshark"  #this is only for windows
    cmdstr = 'start /WAIT "" "%s/tshark.exe" -2 -r "%s" -R "%s" -w "%s" -F pcap'%(Wireshark_path,pcapfile,cmd_filter,Temp_pcap_File)
    os.system(cmdstr)
    
    #2, generate XMLs, and every XML has two version, one for string type, another for blob type.
    
    packets = rdpcap("c:\\test\\target.pcap")#erro here, because the magic of generated pcap file by tshark is 0d 0a 0d 0a 60 00 00 00. 

    
    packets = rdpcap(Temp_pcap_File)
    i = 0
    j = 0

    for packet_content in packets:
        packet_list = []
        if packet_content.haslayer(TCP):
            packet_payload = str(packet_content.getlayer(TCP).payload)
            #1.tcp
            port = packet_content.dport
            commandline_str ="""			<Param name="CommandLine" value="C:\\Program Files\\aMule\\amule.exe"/> """
            publisher_str = """
            <Publisher class="udp.Udp">
                    <Param name="host" value="127.0.0.1" />
                    <Param name="port" value="%d" />
            </Publisher>

            """%port

            hexstr = "".join("{:02x}".format(ord(c)) for c in packet_payload)                
            #2.1 DataModel str
            string_data_str = """        <String valueType="hex" value="%s" /> """%hexstr
            #2.2 DataModel blob
            blob_data_str = """       <Blob name="data" valueType="hex" value="%s" isStatic="true" /> """%hexstr
            
            
            
            #3 generate XML files

            print packet_payload
            
            a_XML = XML_0 + string_data_str + XML_1 + commandline_str + XML_2 + publisher_str  + XML_3 + logger_str_win + XML_4
            b_XML = XML_0 + blob_data_str   + XML_1 + commandline_str + XML_2 + publisher_str  + XML_3 + logger_str_win + XML_4
            #tcp
            #generate XML files
            #and so on ...
            a_xmlname = "XMLs//" + str(j) + "_%s_str_tcp.xml"%target_name
            b_xmlname = "XMLs//" + str(j) + "_%s_blob_tcp.xml"%target_name
            fp_a = open(a_xmlname, "w+")
            fp_b = open(b_xmlname, "w+")
            fp_a.write(a_XML)
            fp_b.write(b_XML)
            fp_a.close()
            fp_b.close()
            i = i + 1




        if packet_content.haslayer(UDP):
            packet_payload = str(packet_content.getlayer(UDP).payload)
            print packet_payload
            #1.udp
            port = packet_content.dport
            commandline_str ="""			<Param name="CommandLine" value="C:\\Program Files\\aMule\\amule.exe"/> """
            publisher_str = """
            <Publisher class="tcp.Tcp">
                    <Param name="host" value="127.0.0.1" />
                    <Param name="port" value="%d" />
            </Publisher>

            """%port

            
            hexstr = "".join("{:02x}".format(ord(c)) for c in packet_payload)                
            #2.1 DataModel str
            string_data_str = """        <String valueType="hex" value="%s" /> """%hexstr
            #2.2 DataModel blob
            blob_data_str = """       <Blob name="data" valueType="hex" value="%s" isStatic="true" /> """%hexstr
            
            #3 generate XML files

            print packet_payload
            
            a_XML = XML_0 + string_data_str + XML_1 + commandline_str + XML_2 + publisher_str  + XML_3 + logger_str_win + XML_4
            b_XML = XML_0 + blob_data_str   + XML_1 + commandline_str + XML_2 + publisher_str  + XML_3 + logger_str_win + XML_4
            #tcp
            #generate XML files
            #and so on ...
            a_xmlname = "XMLs//" + str(j) + "_%s_str_udp.xml"%target_name
            b_xmlname = "XMLs//" + str(j) + "_%s_blob_udp.xml"%target_name
            fp_a = open(a_xmlname, "w+")
            fp_b = open(b_xmlname, "w+")
            fp_a.write(a_XML)
            fp_b.write(b_XML)
            fp_a.close()
            fp_b.close()
            j = j + 1




if __name__ == "__main__":
    global pcapfile
    genXMLs(pcapfile)