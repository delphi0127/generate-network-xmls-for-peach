// killall.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include <windows.h>
#include <psapi.h>

BOOL IsWantedProcess(DWORD pid, TCHAR* name)
{
	TCHAR szProcessName[MAX_PATH] = TEXT("<unknown>");
	HMODULE hMod;
	HANDLE hProcess;
	DWORD cbNeeded;
	unsigned int i;
	int ret = 0;
	
	hProcess = OpenProcess(PROCESS_QUERY_INFORMATION|PROCESS_VM_READ, FALSE, pid);
	if(hProcess == NULL)
		return 0;
	
	if( EnumProcessModules(hProcess, &hMod, sizeof(hMod), &cbNeeded))
	{
		GetModuleBaseName( hProcess, hMod, szProcessName, 
			sizeof(szProcessName)/sizeof(TCHAR) );

		if(_tcsstr(szProcessName, name) != 0)
		{
			ret = 1;
		}
	}

	CloseHandle(hProcess);
	return ret;
}

void KillPid(DWORD pid)
{
	HANDLE hProcess;
	unsigned int i;
	
	hProcess = OpenProcess(PROCESS_TERMINATE, FALSE, pid);
	if(hProcess == NULL)
		return;
	
	TerminateProcess(hProcess, 0);
	
	CloseHandle(hProcess);
}

int _tmain(int argc, _TCHAR* argv[])
{
	DWORD	pids[1024];
	DWORD	pBytesReturned;

	EnumProcesses(pids, sizeof(pids), &pBytesReturned);

	if(argc <= 1)
	{
		_tprintf(TEXT("killall.exe v0.1\n"));
		_tprintf(TEXT("Copyright (c) 2007 Michael Eddington\n\n"));
		_tprintf(TEXT("Syntax error: killall.exe <process name>\n"));
		exit(0);
	}

	for(int i = 0; i< (pBytesReturned/sizeof(DWORD)); i++)
	{
		if(IsWantedProcess(pids[i], argv[1]))
		{
			KillPid(pids[i]);
		}
	}
	
	return 0;
}

// end
