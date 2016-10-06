// The following ifdef block is the standard way of creating macros which make exporting 
// from a DLL simpler. All files within this DLL are compiled with the CTYPESHELPER_EXPORTS
// symbol defined on the command line. this symbol should not be defined on any project
// that uses this DLL. This way any other project whose source files include this file see 
// CTYPESHELPER_API functions as being imported from a DLL, whereas this DLL sees symbols
// defined with this macro as being exported.
#ifdef CTYPESHELPER_EXPORTS
#define CTYPESHELPER_API __declspec(dllexport)
#else
#define CTYPESHELPER_API __declspec(dllimport)
#endif

struct TestCase1
{
	short	Val1;
	int		Val2;
};

struct TestCase2
{
	char	byte1;
};

struct TestCase3
{
	char	byte1;
	char	byte2;
	char	byte3;
	struct TestCase1 case1;
};

struct TestCase4
{
	char	byte1;
	struct TestCase2* case2;
	struct TestCase1* case1;
	char	byte2;
};

struct Context
{
	DWORD context;
	DWORD tlscontext;
	DWORD connection;
};

CTYPESHELPER_API int TestCase1(struct TestCase1 value);
CTYPESHELPER_API struct Context* TestCase1_1(struct TestCase1* value);
CTYPESHELPER_API int TestCase2(struct TestCase2 value);
CTYPESHELPER_API int TestCase3(struct TestCase3 value);
CTYPESHELPER_API int TestCase4(struct TestCase4 value);

// end
