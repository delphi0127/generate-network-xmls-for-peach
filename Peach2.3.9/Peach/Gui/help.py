'''
Help strings for the GUI.

@author: Michael Eddington
@version: $Id: help.py 808 2008-03-25 18:56:36Z meddingt $
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
#   Blake Frantz(blakefrantz@gmail.com)	
# $Id: help.py 808 2008-03-25 18:56:36Z meddingt $


HelpTreeNodes = {
	"Peach" : "",
	"Template" : "Templates are top level elements that contain other data elements. Templates can be based on other Templates or Blocks using the ref attribute. Templates behave much like Blocks.",
	"Block" : "Blocks are combinations of other data elements combined in sequence to produce a block of data. A block is similar to a c structure. Blocks can contain other blocks, strings, numbers, etc.",
	"Number" : "Represents a non-ascii integer that has a size in bits, and a byte order.",
	"Sequence" : "Specify a sequence of elements that will be used in order. An example use would be generating first IPv4 addresses, then IPv6 addresses.",
	"Choice" : "A choice will choose zero or more of the elements it contains based on minOccurs and maxOccurs.",
	"String" : "A string of characters. This string element can represent both char and wchar strings.",
	"Relation" : "Describes relations between different data elements. Relations currently supported are \"size\" and \"count\".",
	"Flags": "Define a set of bit flags. Supports multiple bit flags.",
	"Flag" : "A one or more bit flag that is part of a flag set (Flags element).",
	"Data" : "Specified a set of default data values for a template.",
	"Blob" : "A piece of binary data specified in hex.",
	"Include" : "Imports other Peach XML files into a namespace. This allows reusing existing templates from other Peach XML files.",
	"PythonPath" : "Includes an additional path for module resolution. Synonomis with saying \"sys.path.append()\".",
	"Import" : "Import a python file into the current context. This allows referencing generators and methods in external python files. Synonomis with saying \"import xyz\".",
	"Test" : "Define a test to run. Currently a test is defined as a combination of a Template and optionally a Data set. In the future this will expand to include a state model, defaults for generation, etc.",
	"Publisher" : "Define the publisher to use for this test. A publisher sends and receives data. This can take the form of a network protocol (TCP, UDP, HTTP) or calling an API/DLL or COM control. For testing purposes there are publishers that will simply output the generated data to the console.",
	"Param" : "Param elements provide parameters for the parent element. It is possible to pass python types like arrays by specifying valueType as literal and providing python literal as value. e.g. &quot;[ 1, 2, 3, 4 ]&quot; would be an array.",
	"Run" : "A collection of tests to run at once. The run name &quot;DefaultRun&quot; is special and will be run if no other run name is provided.",
	"Generator" : "Attach a Peach generator to a data element. This can be any existing generator or a custom generator.",
	"Transformer" : "Transform data into another format. This can include encoding it in some way (base64), compressing it (gzip), etc.",
	"Agent" : "Configure a local or remote agent. Agents can perform variouse tasks during a fuzzing run. This element must include at least one Monitor child.",
	"Monitor" : "Monitors are agent modules that can perform a number of tasts such as monitoring a target application to detect faults, restarting virtual machines, recording network traffice, etc. Custom monitors can easily be created and used along with the included monitors.",
	"StateMachine" : "Defines a state machine to use during a fuzzing test.  State machines in Peach are intended to be fairly simple and allow for only the basic modeling typically required for fuzzing state aware protocols or call sequences.  State machines are made up of one or more States which are inthem selves make up of one or more Action.  As Actions are executed the data can be moved between them as needed.",
	"State" : "The State element defines a sequence of Actions to perform.  Actions can cause a change to another State.  Such changes can occur dynamically based on content received or sent by attaching python expressions to actions via the onStart/onComplete/when attributes.",
	"Action" : "Defines an action to perform in this state.  Actions are things such as send output, receive input, or change state.  Actions are performed top down.",
	"Action-Param" : "Define a parameter for call.  Parameters are passed in the order they appear.",
	"Action-Result" : "Used to capture return value of call."
	}

HelpPropertyItems = {
	"String" : {
		"type" : "Specify type of string. Default is char.",
		"length" : "Specify static length of string. Default is unbounded.",
		"tokens" : "Specify the set of tokens (as a Python array literal) that will be used to tokenize and fuzz this String. Example: &quot;[':', '.', '[' ]&quot;",
		"nullTerminated" : "Indicate if string is null terminated. Default is false.",
		"isStatic" : "Indicates value is static and should not be fuzzed.",
		"padCharacter" : "Specify the character to bad the string with if it's length if less then specified in the length attribute. Only valid when the length attribute is also specified.",
		},
	
	"Number" : {
		"valueType" : "Specify the format of the number as String, Hex, or Literal value.",
		"size" : "Specify the width of the number in bits.",
		"endian" : "Specify the byte order.",
		"signed" : "Specify whether the Number is signed or unsigned",
		},

	"Flags" : {
		"size" : "Specify the width of this field in bits.",
		"endian" : "Specify the byte order or this field.",
		},
	}

EnumDropDowns = {
	"Generator" : {
		"class" : [
			"AsInt16",
			"AsInt24",
			"AsInt32",
			"AsInt4x4",
			"AsInt64",
			"AsInt8",
			"BadBerEncodedOctetString",
			"BadDate",
			"BadDerEncodedOctetString",
			"BadFilename",
			"BadHostname",
			"BadIpAddress",
			"BadNumbers",
			"BadNumbers16",
			"BadNumbers24",
			"BadNumbers32",
			"BadNumbers8",
			"BadNumbersAsString",
			"BadPath",
			"BadPositiveNumbers",
			"BadString",
			"BadStrings",
			"BadTime",
			"BadUnicode",
			"BadUnsignedNumbers",
			"BadUnsignedNumbers16",
			"BinaryList",
			"Bit",
			"Block",
			"Block2",
			"Block3",
			"BlockRandomizer",
			"BlockSize",
			"Dictionary",
			"Double",
			"EndlessRandomStrings",
			"EndlessRandomWideStrings",
			"FixedLengthString",
			"FlagPermutations",
			"FlagSet",
			"Flags",
			"Flags2",
			"Float",
			"GeneratorChoice",
			"GeneratorList",
			"GeneratorList2",
			"GeneratorListGroupMaster",
			"GeneratorListGroupSlave",
			"GoodUnicode",
			"IcmpChecksum",
			"Incrementor",
			"Int16",
			"Int32",
			"Int64",
			"Int8",
			"List",
			"MultiBlock",
			"MultiBlockCount",
			"NumberLimiter",
			"NumberVariance",
			"NumbersVariance",
			"OverLongUtf8",
			"PerCallIncrementor",
			"PerRoundIncrementor",
			"PrintStderr",
			"PrintStdout",
			"PseudoRandomNumber",
			"Repeater",
			"RepeaterGI",
			"SequentialFlipper",
			"Static",
			"StaticBinary",
			"StringTokenFuzzer",
			"StringVariance",
			"TopLevelDomains",
			"WithDefault",
			"Wrap",
			]
		},
	
	"Publisher" : {
		"class" : [
			"tcp.Tcp",
			"udp.Udp",
			"process.Command",
			"stdout.Stdout",
			"file.File",
			"file.FilePerIteration",
			"sql.Odbc",
			"com.Com",
			"Publisher",
			]
		},
	
	"Logger" : {
		"class" : [
			"logger.Filesystem"
			]
		},
	
	"Transformer" : {
		"class" : [
			"asn1.DerEncodeOctetString",
			"asn1.DerEncodeInteger",
			"asn1.BerEncodeOctetString",
			"asn1.BerEncodeInteger",
			"asn1.CerEncodeOctetString",
			"asn1.CerEncodeInteger",
			"compress.GzipCompress",
			"compress.GzipDecompress",
			"compress.Bz2Compress",
			"compress.Bz2Decompress",
			"crypto.Crypt",
			"crypto.UnixMd5Crypt",
			"crypto.ApacheMd5Crypt",
			"crypto.CvsScramble",
			"crypto.Md5",
			"crypto.Sha1",
			"crypto.Hmac",
			"encode.SidStringToBytes",
			"encode.WideChar",
			"encode.UrlEncode",
			"encode.NetBiosDecode",
			"encode.NetBiosEncode",
			"encode.UrlEncodePlus",
			"encode.Base64Encode",
			"encode.Base64Decode",
			"encode.HtmlEncodeAgressive",
			"encode.HtmlDecode",
			"encode.Utf16",
			"encode.Utf16Le",
			"encode.Utf16Be",
			"encode.Ipv4StringToOctet",
			"encode.Ipv4StringToNetworkOctet",
			"encode.Ipv6StringToOctet",
			"encode.Hex",
			"encode.HexString",
			"type.NumberToString",
			"type.StringToInt",
			"type.StringToFloat",
			"type.IntToHex",
			"type.AsInt8",
			"type.AsInt16",
			"type.AsInt24",
			"type.AsInt32",
			"type.AsInt64",
			]
		},
	
	"Monitor" : {
		"class" : [
			"debugger.WindowsDebugger",
			"vm.Vmware",
			"process.PageHeap",
			"process.Process",
			"network.PcapMonitor",
			"memory.Memory",
			"socketmon.SocketMonitor",
			]
		},
	
	"Action" : {
		"type" : [
			"start",
			"connect",
			"accept",
			"close",
			"stop",
			"input",
			"output",
			"call",
			"slurp",
			"changeState",
			]
		},
	
	"Action-Param" : {
		"type" : [
			"in",
			"inout",
			"out",
			]
		},
	}

# end
