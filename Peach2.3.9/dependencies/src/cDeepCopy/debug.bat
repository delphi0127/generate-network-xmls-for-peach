@echo off
python setup.py build --debug
python setup.py install

del c:\Python25\Lib\site-packages\cDeepCopy.*
move c:\Python25\Lib\site-packages\cDeepCopy_d.pdb c:\Python25\Lib\site-packages\cDeepCopy.pdb
move c:\Python25\Lib\site-packages\cDeepCopy_d.pyd c:\Python25\Lib\site-packages\cDeepCopy.pyd

rem END
