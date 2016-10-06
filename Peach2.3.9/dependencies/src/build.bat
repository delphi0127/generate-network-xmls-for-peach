@echo off

rem Build Modules into MSI Installers
rem Copyright (c) Michael Eddington

cd 4Suite-XML-1.0.2
rmdir /s/q build dist
python setup.py bdist_msi
copy dist\*.msi ..
cd ..

cd cDeepCopy
rmdir /s/q build dist
python setup.py bdist_msi
copy dist\*.msi ..
cd ..

cd comtypes-0.6.2
rmdir /s/q build dist
python setup.py bdist_msi
copy dist\*.msi ..
cd ..

cd cPeach
rmdir /s/q build dist
python setup.py bdist_msi
copy dist\*.msi ..
cd ..

cd peach-pypcap
rmdir /s/q build dist
python setup.py config
python setup.py bdist_msi
copy dist\*.msi ..
cd ..

cd psutil-0.2.0
rmdir /s/q build dist
python setup.py bdist_msi
copy dist\*.msi ..
cd ..

cd pyasn1-0.0.13a
rmdir /s/q build dist
python setup.py bdist_msi
copy dist\*.msi ..
cd ..

cd PyDbgEng-0.14
rmdir /s/q build dist
python setup.py bdist_msi
copy dist\*.msi ..
cd ..

cd pyvmware-0.1-src
rmdir /s/q build dist
python setup.py bdist_msi
copy dist\*.msi ..
cd ..

cd zope.interface-3.6.1
rmdir /s/q build dist
python setup.py bdist_msi
copy dist\*.msi ..
cd ..

cd Twisted-10.2.0
rmdir /s/q build dist
python setup.py bdist_msi
copy dist\*.msi ..
cd ..

rem END
