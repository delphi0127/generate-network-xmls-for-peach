@echo off

rem Build the binary version of Peach using py2exe
rem Copyright (c) Michael Eddington

cd c:\peach\tools

xcopy /y/q setup64.py ..

cd c:\peach

del /q bin build dist
rmdir /s/q bin
rmdir /s/q build
rmdir /s/q dist

rem mkdir build\bdist.win-amd64-2.6\msi\Share\4Suite\Schemata
rem copy C:\Python27\Share\4Suite\default.cat build\bdist.win-amd64-2.6\msi\Share\4Suite
rem copy C:\Python27\Share\4Suite\Schemata\*.* build\bdist.win-amd64-2.6\msi\Share\4Suite\Schemata

rem -O0 will cause optmized byte code to be generated
c:\python27\python -OO setup64.py py2exe -p win32com -p twisted

ren dist bin
rmdir /s/q build
del /q setup64.py

rem Extra re-dist files
copy tools\bangexploitable\x64\msec.dll bin

xcopy /s/q c:\peach\Peach\Generators\xmltests c:\peach\bin\xmltests\

if "%1"==all call c:\peach\tools\gendocs.bat
if "%1"==bin goto BINONLY

goto EXIT

:BINONLY

cd c:\peach
xcopy /y/q C:\peach\Peach\Engine\PeachTypes.xml
rmdir /s/q dependencies
rmdir /s/q Peach
rmdir /s/q test
del /q *.py
del /q *.pyw

:EXIT

rem ALl done!
