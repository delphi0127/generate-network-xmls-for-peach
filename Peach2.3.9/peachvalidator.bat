@echo off

if exist %~dp0\bin\peach.exe %~dp0\bin\peachvalidator.exe %1 %2 %3 %4 %5 %6 %7 %8 %9
if not exist %~dp0\bin\peach.exe pythonw %~dp0\peachvalidator.pyw %1 %2 %3 %4 %5 %6 %7 %8 %9
