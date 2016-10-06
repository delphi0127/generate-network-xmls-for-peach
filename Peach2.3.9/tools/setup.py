from distutils.core import setup
import py2exe
import Ft.Lib.DistExt.Py2Exe
import glob, sys, os

sys.path.append("C:\\Program Files\\Microsoft Visual Studio 9.0\\VC\\redist\\x86\\Microsoft.VC90.CRT")

setup(
	options={"py2exe": {"optimize":2, "bundle_files":3}},
	console=['peach.py', 'minset.py'],
	windows=['peachvalidator.pyw'],
	
	data_files=[
			("",
			  ["peach.xsd"],
			  ["readme.html"],
			  ["template.xml"],
			  ["defaults.xml"],
			  ),
			("icons", glob.glob("peach/gui/icons/*")),
			("Microsoft.VC90.CRT", glob.glob(r'C:\Program Files\Microsoft Visual Studio 9.0\VC\redist\x86\Microsoft.VC90.CRT\*.*'))
		]
	)

# end
