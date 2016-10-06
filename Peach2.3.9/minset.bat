@echo off

if exist %~dp0\bin\minset.exe %~dp0\bin\minset.exe %1 %2 %3 %4 %5 %6 %7 %8 %9
if not exist %~dp0\bin\minset.exe python %~dp0\tools\minset\minset.py %1 %2 %3 %4 %5 %6 %7 %8 %9

