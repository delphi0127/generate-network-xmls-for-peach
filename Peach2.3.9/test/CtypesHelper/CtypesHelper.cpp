// CtypesHelper.cpp : Defines the exported functions for the DLL application.
//

#include "stdafx.h"
#include "CtypesHelper.h"
#include <stdlib.h>
#include <stdio.h>

CTYPESHELPER_API int TestCase1(struct TestCase1 value)
{
	if(value.Val1 == 0xffe && value.Val2 == 0xfffffe)
	{
		printf("TestCase1 Passed\n");
		return 1;
	}

	printf("TestCase1 Failed\n");
	return 0;
}

CTYPESHELPER_API struct Context* TestCase1_1(struct TestCase1* value)
{
	struct Context* c;

	if(value->Val1 == 0xffe && value->Val2 == 0xfffffe)
	{

		c = (struct Context*) malloc(sizeof(struct Context));
		c->connection = 1;
		c->context = 2;
		c->tlscontext = 4;

		printf("TestCase1_1 Passed %u\n", c);
		return c;
	}

	printf("TestCase1_1 Failed\n");
	return NULL;
}

CTYPESHELPER_API int TestCase2(struct TestCase2 value)
{
	if(value.byte1 == (char)0xfe)
	{
		printf("TestCase2 Passed\n");
		return 1;
	}

	printf("TestCase2 Failed: %d vs. %d\n", value.byte1, (char)0xfe);
	return 0;
}

CTYPESHELPER_API int TestCase3(struct TestCase3 value)
{
	if(value.byte1 == (char)0xfe && value.byte2 == (char)0xef && value.byte3 == (char)0 && 
		value.case1.Val1 == (short)0xffe && value.case1.Val2 == (int)0xfffffe)
	{
		printf("TestCase3 Passed\n");
		return 1;
	}

	printf("TestCase3 Failed\n");
	return 0;
}

CTYPESHELPER_API int TestCase4(struct TestCase4 value)
{
	if(value.byte1 == (char)0xfe && value.byte2 == (char)0xef && 
		value.case1->Val1 == (short)0xffe && value.case1->Val2 == (int)0xfffffe)
	{
		printf("TestCase4 Passed\n");
		return 1;
	}

	printf("TestCase4 Failed %d %d %d %d\n", value.byte1, value.byte2, value.case1->Val1, value.case1->Val2);
	return 0;
}

CTYPESHELPER_API int TestCase4_1(struct TestCase4** value)
{
	if((*value)->byte1 == (char)0xfe && (*value)->byte2 == (char)0xef && 
		(*value)->case1->Val1 == (short)0xffe && (*value)->case1->Val2 == (int)0xfffffe)
	{
		printf("TestCase4_1 Passed\n");
		return 1;
	}

	printf("TestCase4_1 Failed %d %d %d %d\n", (*value)->byte1, (*value)->byte2, (*value)->case1->Val1, (*value)->case1->Val2);
	return 0;
}

// end
