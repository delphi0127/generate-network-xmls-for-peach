
//
// PIN Tool to find all basic blocks a program hits.
//  This PIN Tool is intended for use with Peach.
//
//  Code based on examples from PIN documentation.
//
// Author:
//   Michael Eddington (mike@phed.org)
//

#include <iostream>
#include <fstream>
#include <pin.H>
#include <stdio.h>
#include <set>

using namespace std;

static FILE* trace;
static set<unsigned int> setKnownBlocks;
static pair<set<unsigned int>::iterator,bool> ret;
static set<unsigned int>::iterator itr;
int haveExisting = FALSE;

VOID PIN_FAST_ANALYSIS_CALL rememberBlock(ADDRINT bbl)
{
	ret = setKnownBlocks.insert(bbl);
	if(ret.second == true)
	{
		fprintf(trace, "%p\n", bbl);
		fflush(trace);
	}
}

VOID Trace(TRACE trace, VOID *v)
{
	// Q: Will this loop be faster if we remove known blocks from our set after adding them?
	//    In theory we should only hit each bbl once and so the set would get smaller providing
	//    faster lookup operations.

	for (BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl))
	{
		if(!haveExisting || setKnownBlocks.find(BBL_Address(bbl)) == setKnownBlocks.end())
			BBL_InsertCall(bbl, IPOINT_ANYWHERE, AFUNPTR(rememberBlock), IARG_FAST_ANALYSIS_CALL, IARG_ADDRINT, BBL_Address(bbl), IARG_END);
	}
}

VOID Fini(INT32 code, VOID *v)
{
	fclose(trace);
}

int main(int argc, char * argv[])
{
	// Load existing trace
	unsigned int block = 0;
	FILE* fd = fopen("bblocks.existing", "rb+");
	if(fd != NULL)
	{
		haveExisting = TRUE;
		while(!feof(fd))
		{
			if(fscanf(fd, "%x\n", &block) < 4)
			{
				setKnownBlocks.insert(block);
			}
		}
	}

	trace = fopen("bblocks.out", "w");
	
	PIN_Init(argc, argv);
	TRACE_AddInstrumentFunction(Trace, 0);
	PIN_AddFiniFunction(Fini, 0);
	PIN_StartProgram();

	return 0;
}

// end
