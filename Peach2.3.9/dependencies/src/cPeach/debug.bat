@echo off
setup.py build --debug
setup.py install

del c:\Python25\Lib\site-packages\cPeach.*
move c:\Python25\Lib\site-packages\cPeach_d.pdb c:\Python25\Lib\site-packages\cPeach.pdb
move c:\Python25\Lib\site-packages\cPeach_d.pyd c:\Python25\Lib\site-packages\cPeach.pyd

rem END
