@echo off

rem Build the binary version of Peach using py2exe
rem Copyright (c) Michael Eddington

cd c:\peach\tools

copy /y setup.py ..

cd c:\peach

rmdir /s/q bin
rmdir /s/q build
rmdir /s/q dist

copy tools\minset\minset.py

rem -O0 will cause optmized byte code to be generated
python -OO setup.py py2exe -p win32com -p twisted
del /q minset.py
ren dist bin
rmdir /s/q build
del /q setup.py

rem Extra re-dist files
copy C:\Python27\Lib\site-packages\wx-2.8-msw-unicode\wx\gdiplus.dll bin
copy c:\windows\system32\MFC71.DLL bin
copy c:\windows\SysWOW64\mfc71.dll bin
del /q bin\iphlpapi.dll
copy tools\bangexploitable\x86\msec.dll bin
copy tools\minset\BasicBlocks\BasicBlocks\bin\release\*.* bin

xcopy /s/q c:\peach\Peach\Generators\xmltests c:\peach\bin\xmltests\

if "%1"==all call c:\peach\tools\gendocs.bat
if "%1"==bin goto BINONLY

goto EXIT

:BINONLY

cd c:\peach
copy /y C:\peach\Peach\Engine\PeachTypes.xml
rmdir /s/q dependencies
rmdir /s/q Peach
rmdir /s/q test
del /y *.py
del /y *.pyw

:EXIT

rem ALl done!
