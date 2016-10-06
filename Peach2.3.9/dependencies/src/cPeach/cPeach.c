
// Native Peach Methods
// Author: Michael Eddington (mike@phed.org)

#include <Python.h>
#define VERSION "0.1"
#define MODULE "cPeach"

static PyObject*	moduleError = NULL;
static PyObject*	DataElement = NULL;
static PyObject*	Relation = NULL;
static PyObject*	Block = NULL;
static PyObject*	Template = NULL;

static char *moduleDoc = "Native Peach Methods";

static PyObject* _findDataElementByName(PyObject* self, PyObject* names);

static PyObject* _getRootOfDataMap(PyObject* self)
{
	PyObject*	root = NULL;
	PyObject*	parent = NULL;

	root = self;
	Py_XINCREF(root);	// INC REF

	parent = PyObject_GetAttrString(root, "parent");	// NEW REF
	while(parent && parent != Py_None && PyObject_IsInstance(parent, DataElement))
	{
		Py_XDECREF(root);	// DEC REF
		root = parent;
		parent = PyObject_GetAttrString(root, "parent");	// NEW REF
	}

	Py_XDECREF(parent); // DEC REF
	return root;
}

static PyObject* _getAllRelationsInDataModel(PyObject* self, PyObject* node, int (*Yield)(void** args, PyObject* relation), void** YieldData)
{
	PyObject*	relationCache = NULL;
	PyObject*	root = NULL;
	PyObject*	item = NULL;
	PyObject*	tmp = NULL;
	PyObject*	children = NULL;
	Py_ssize_t	cnt = 0;
	Py_ssize_t	i = 0;

	if(!node || node == Py_None)
	{
		node = _getRootOfDataMap(self);	// NEW
	}
	else
		Py_XINCREF(node);	// INC
	
	//# Use cache if we have it
	if (PyObject_IsInstance(node, DataElement))
	{
		relationCache = PyObject_GetAttrString(node, "relationCache");	// NEW
		if(relationCache && relationCache != Py_None)
		{
			root = _getRootOfDataMap(self);	// NEW
			
			for(cnt = PyList_GET_SIZE(relationCache), i=0; i<cnt; i++)
			{
				item = PyList_GET_ITEM(relationCache, i);	// BORROW
				if(item == 0 || item == Py_None)
				{
					fprintf(stderr, "_getAllRelationsInDataModel: Warning item #%d is null or None\n", i);
					continue;
				}

				item = PyObject_CallMethod(root, "getDataElementByName", "O", item); // NEW
				if(item == 0 || item == Py_None)
				{
					// This is okay, it can happen sometimes due to "when" relations that cause
					// trimming of the tree after an "input" action or loading a data set.
					continue;
				}

				if(Yield(YieldData, item))
				{
					Py_XDECREF(node);
					Py_XDECREF(relationCache);
					Py_XDECREF(root);
					return item;
				}
				
				Py_XDECREF(item);
			}

			Py_XDECREF(node);
			Py_XDECREF(relationCache);
			Py_XDECREF(root);

			return NULL;
		}

		if(relationCache)
			Py_XDECREF(relationCache);
	}

	if (PyObject_IsInstance(node, Relation))
	{
		if(Yield(YieldData, node))
			return node;

		Py_XDECREF(node);
		return NULL;
	}

	if (PyObject_IsInstance(node, DataElement))
	{
		PyObject* relation;
		children = PyObject_GetAttrString(node, "_children");	// NEW REF
		
		for(cnt = PyList_GET_SIZE(children), i = 0; i<cnt; i++)
		{
			item = PyList_GET_ITEM(children, i);
			if(!item || item == Py_None)
			{
				fprintf(stderr, "_getAllRelationsInDataModel: Warning item #%d is null or None (spot 3)\n", i);
				continue;
			}

			relation = _getAllRelationsInDataModel(self, item, Yield, YieldData);	// NEW
			if(relation)
			{
				Py_XDECREF(children);
				Py_XDECREF(node);

				return relation;
			}
		}

		Py_XDECREF(children);
	}

	Py_XDECREF(node);
	return NULL;
}

static PyObject* _getRelationsInDataModelFromHere(PyObject* self, PyObject* node, int (*Yield)(void** self, PyObject* relation), void** YieldData)
{
	PyObject*	relation;
	PyObject*	parent;
	PyObject*	cur;
	PyObject*	tmp;

	if(!node || node == Py_None)
	{
		node = self;
	}

	parent = PyObject_GetAttrString(node, "parent");	// NEW
	if(!PyObject_IsInstance(parent, DataElement))
	{
		Py_XDECREF(parent);
		return _getAllRelationsInDataModel(self, node, Yield, YieldData);
	}

	// If not start searching
	cur = parent;
	parent = NULL;

	while(cur && cur != Py_None && PyObject_IsInstance(cur, DataElement))
	{
		relation = _getAllRelationsInDataModel(self, cur, Yield, YieldData);	// NEW
		if(relation)
		{
			Py_XDECREF(cur);
			return relation;
		}

		tmp = cur;
		cur = PyObject_GetAttrString(cur, "parent");	// NEW

		Py_XDECREF(tmp);
	}

	Py_XDECREF(cur);
	return NULL;
}

static PyObject* _getOfElement(PyObject* self)
{
	//if self.of == None:
	//	return None
	//
	//obj = self.parent.findDataElementByName(self.of)
	//if obj == None:
	//	# Could element have become an array?
	//	obj = self.parent.findArrayByName(self.of)
	//
	//return obj

	PyObject*	of;
	PyObject*	obj;
	PyObject*	ofArray;
	
	of = PyObject_GetAttrString(self, "of");	// NEW
	if(!of || of == Py_None)
		Py_RETURN_NONE;
	
	ofArray = PyObject_CallMethod(of, "split", "O", PyString_FromString("."));	// NEW
	obj = _findDataElementByName(self, ofArray);	// NEW
	
	Py_XDECREF(ofArray);
	ofArray = NULL;

	if(!obj || obj == Py_None)
	{
		// Could element have become an array?
		PyObject*	parent;

		parent = PyObject_GetAttrString(self, "parent");	// NEW
		if(!parent)
		{
			Py_XDECREF(of);
			Py_RETURN_NONE;
		}

		obj = PyObject_CallMethod(parent, "findArrayByName", "O", of);	// NEW
		Py_XDECREF(parent);
	}

	Py_XDECREF(of);
	return obj;
}

// FALSE -- Continue; TRUE -- Stop and pump value up
static int MyYield(void** args, PyObject* relation)
{
	PyObject*	of;
	PyObject*	rType;
	PyObject*	self = (PyObject*) (args[0]);
	PyObject*	type = (PyObject*) (args[1]);

	of = _getOfElement(relation);	// NEW
	if(!PyObject_Compare(self, of))
	{
		rType = PyObject_GetAttrString(relation, "type");	// NEW
		if(type == Py_None || !PyObject_Compare(rType, type))
		{
			Py_XDECREF(rType);
			Py_XDECREF(of);

			//fprintf(stderr, "MyYield: Returning true\n");
			return -1;
		}

		Py_XDECREF(rType);
	}

	Py_XDECREF(of);
	
	return 0;
}

static PyObject* _getRelationOfThisElement(PyObject* self, PyObject* type)
{
	PyObject*	r;
	PyObject*	args[2];
	args[0] = self;
	args[1] = type;

	r = _getRelationsInDataModelFromHere(self, NULL, &MyYield, args);	// NEW
	if(!r || r == Py_None)
		Py_RETURN_NONE;

	return r;
}

/* **************************************************************************** */

static int PyStrCmp(PyObject* str1, PyObject* str2)
{
	void*	buff1;
	void*	buff2;
	Py_ssize_t	buff1Len;
	Py_ssize_t	buff2Len;
	
	PyObject_AsReadBuffer(str1, &buff1, &buff1Len);
	PyObject_AsReadBuffer(str2, &buff2, &buff2Len);

	if(buff1Len != buff2Len)
		return 1;
	
	return memcmp(buff1, buff2, buff1Len);

	//fprintf(stderr, "Comparing [%s] and [%s] (%d)\n", 
	//	PyString_AS_STRING(str1), 
	//	PyString_AS_STRING(str2), 
	//	strcmp(PyString_AS_STRING(str1), PyString_AS_STRING(str2))
	//	);

	//return strcmp(PyString_AS_STRING(str1), PyString_AS_STRING(str2));
}

static PyObject* __findDataElementByName(PyObject* self, PyObject* name)
{
	//# look at us!
	//if node.name == name:
	//	yield node
	//
	//# look at each child
	//if node._childrenHash.has_key(name):
	//	yield node[name]
	//
	//# search down each child path
	//for child in node._children:
	//	if isinstance(child, DataElement) and child not in hist:
	//		hist.append(child)
	//		for n in self._findDataElementByName(child, name, hist):
	//			yield n
	//
	//# done!

	PyObject*	ret = NULL;
	PyObject*	selfName = NULL;
	PyObject*	_childrenHash = NULL;
	PyObject*	_children = NULL;
	PyObject*	child = NULL;
	PyObject*	childRet = NULL;

	Py_ssize_t	cnt = 0;
	Py_ssize_t	i = 0;
	Py_ssize_t	cnt2 = 0;
	Py_ssize_t	x = 0;

	ret = PyList_New(0);	// NEW

	selfName = PyObject_GetAttrString(self, "name");	// NEW
	if( !PyStrCmp(selfName, name) )
		PyList_Append(ret, self);
	
	Py_XDECREF(selfName);	// DEC
	selfName = NULL;

	_childrenHash = PyObject_GetAttrString(self, "_childrenHash");	// NEW
	if(!_childrenHash)
	{
		PyErr_Clear();
		return ret;
	}

	if(PyDict_Contains(_childrenHash, name))
		PyList_Append(ret, PyDict_GetItem(_childrenHash, name));

	Py_XDECREF(_childrenHash);	// DEC
	_childrenHash = NULL;
	
	_children = PyObject_GetAttrString(self, "_children");	// NEW
	if(!_children)
	{
		PyErr_Clear();
		return ret;
	}

	cnt = PyList_GET_SIZE(_children);

	for(i = 0; i<cnt; i++)
	{
		child = PyList_GET_ITEM(_children, i);
		childRet = __findDataElementByName(child, name);	// NEW
		
		// Append results to our list
		cnt2 = PyList_GET_SIZE(childRet);
		for(x = 0; x < cnt2; x++)
			PyList_Append(ret, PyList_GET_ITEM(childRet, x));

		Py_XDECREF(childRet);
		childRet = NULL;
	}

	Py_XDECREF(_children);
	_children = NULL;

	return ret;
}

static PyObject* _findAllBlocksGoingUp(PyObject* self)
{
	//obj = self
	//if isinstance(obj, Block) or isinstance(obj, Template):
	//	yield obj
	//
	//while obj.parent != None and isinstance(obj.parent, DataElement):
	//	obj = obj.parent
	//	
	//	if isinstance(obj, Block) or isinstance(obj, Template):
	//		yield obj

	PyObject*	ret = NULL;
	PyObject*	obj = NULL;
	PyObject*	tmp = NULL;

	ret = PyList_New(0);	// NEW

	obj = self;
	Py_XINCREF(obj); // INC REF

	if(obj && (PyObject_IsInstance(obj, Block) || PyObject_IsInstance(obj, Template)))
	{
		PyList_Append(ret, obj);
	}

	while(1)
	{
		tmp = obj;
		obj = PyObject_GetAttrString(obj, "parent");	// NEW REF
		Py_XDECREF(tmp);

		if(!obj || !PyObject_IsInstance(obj, DataElement))
			break;

		if(obj && (PyObject_IsInstance(obj, Block) || PyObject_IsInstance(obj, Template)) )
		{
			PyList_Append(ret, obj);
		}
	}

	Py_XDECREF(obj);
	obj = NULL;

	return ret;
}

static PyObject* _checkDottedName(PyObject* node, PyObject* names)
{
	//if node.name != names[0]:
	//	return None
	//
	//obj = node
	//for i in range(1, len(names)):
	//	if not obj.has_key(names[i]):
	//		return None
	//	
	//	obj = obj[names[i]]
	//
	//return obj

	PyObject*	name = NULL;
	PyObject*	_childrenHash = NULL;
	Py_ssize_t	namesCnt = 0;
	Py_ssize_t	i = 0;

	name = PyObject_GetAttrString(node, "name");	// NEW
	if( PyStrCmp(PyList_GET_ITEM(names, 0), name) )
	{
		Py_XDECREF(name);
		return NULL;
	}

	Py_XDECREF(name);	// DEC
	name = NULL;

	namesCnt = PyList_GET_SIZE(names);
	for(i = 1; i<namesCnt; i++)
	{
		name = PyList_GET_ITEM(names, i);

		_childrenHash = PyObject_GetAttrString(node, "_childrenHash");	// NEW
		if(!_childrenHash)
		{
			PyErr_Clear();
			return NULL;
		}

		if(!PyDict_Contains(_childrenHash, name))
		{
			Py_XDECREF(_childrenHash);
			return NULL;
		}

		node = PyDict_GetItem(_childrenHash, name);
		Py_XDECREF(_childrenHash);
	}
	
	Py_XINCREF(node);
	return node;
}

static PyObject* _findDataElementByName(PyObject* self, PyObject* names)
{
	//for block in self._findAllBlocksGoingUp():
	//	#print "findDataElementByName: Looking for %s in %s" % (name, block.name)
	//	for node in self._findDataElementByName(block, names[0]):
	//		obj = self._checkDottedName(node, names)
	//		if obj != None:
	//			return obj
	//
	//return None

	PyObject*	blocks = NULL;
	PyObject*	block = NULL;
	PyObject*	ret = NULL;
	PyObject*	obj = NULL;
	PyObject*	nameZero = NULL;
	PyObject*	node = NULL;
	
	Py_ssize_t	blocksCnt = 0;
	Py_ssize_t	retCnt = 0;
	Py_ssize_t	i = 0;
	Py_ssize_t	x = 0;

	nameZero = PyList_GET_ITEM(names, 0);

	blocks = _findAllBlocksGoingUp(self);	// NEW
	blocksCnt = PyList_GET_SIZE(blocks);

	for(i = 0; i<blocksCnt; i++)
	{
		block = PyList_GET_ITEM(blocks, i);
		
		ret = __findDataElementByName(block, nameZero);	// NEW
		retCnt = PyList_GET_SIZE(ret);

		for(x = 0; x<retCnt; x++)
		{
			node = PyList_GET_ITEM(ret, x);
			obj = _checkDottedName(node, names);	// NEW

			if(obj)
			{
				Py_XDECREF(blocks);
				Py_XDECREF(ret);
				
				//fprintf(stderr, "_findDataElementByName: Returning match\n");
				return obj;
			}
		}

		Py_XDECREF(ret);
	}

	Py_XDECREF(blocks);
	
	//fprintf(stderr, "_findDataElementByName: No match\n");
	Py_RETURN_NONE;
}



static PyObject* getRootOfDataMap(PyObject* self, PyObject* args)
{
	return PyArg_ParseTuple(args, "O:getRootOfDataMap", &self) ? _getRootOfDataMap(self) : NULL;
}

static PyObject* getRelationOfThisElement(PyObject* self, PyObject* args)
{
	PyObject	*type=NULL;
	return PyArg_ParseTuple(args, "OO:getRelationOfThisElement", &self, &type) ? _getRelationOfThisElement(self, type) : NULL;
}

static PyObject* findDataElementByName(PyObject* self, PyObject* args)
{
	PyObject	*name=NULL;
	return PyArg_ParseTuple(args, "OO:findDataElementByName", &self, &name) ? _findDataElementByName(self, name) : NULL;
}

static struct PyMethodDef moduleMethods[] = {
	{"getRelationOfThisElement",			getRelationOfThisElement,			METH_VARARGS, ""},
	{"getRootOfDataMap",					getRootOfDataMap,					METH_VARARGS, ""},
	{"findDataElementByName",				findDataElementByName,				METH_VARARGS, ""},
	{NULL,	NULL}
};

void initcPeach()
{
	PyObject *m, *d, *v, *_version;

	/* Create the module and add the functions */
	m = Py_InitModule(MODULE, moduleMethods);

	/* Add some symbolic constants to the module */
	d = PyModule_GetDict(m);
	_version = PyString_FromString(VERSION);
	PyDict_SetItemString(d, "_version", _version );
	moduleError = PyErr_NewException(MODULE ".Error",NULL,NULL);
	PyDict_SetItemString(d, "Error", moduleError);
	PyDict_SetItemString(d,"error",moduleError);

	/*add in the docstring*/
	v = Py_BuildValue("s", moduleDoc);
	PyDict_SetItemString(d, "__doc__", v);
	Py_XDECREF(v);

	m = PyImport_ImportModule("Peach.Engine.dom");	// NEW REF
	if(!m || m == Py_None)
	{
		fprintf(stderr, "initcPeach(): Error: Failed to import \"Peach.Engine.dom\".\n");
		return;
	}

	DataElement = PyObject_GetAttrString(m, "DataElement");	// NEW REF
	if(!DataElement)
	{
		fprintf(stderr, "initcPeach(): Error: DataElement is null.\n");
	}
	
	Relation = PyObject_GetAttrString(m, "Relation");	// NEW REF
	if(!Relation)
	{
		fprintf(stderr, "initcPeach(): Error: Relation is null.\n");
	}

	Block = PyObject_GetAttrString(m, "Block");	// NEW REF
	if(!Block)
	{
		fprintf(stderr, "initcPeach(): Error: Block is null.\n");
	}

	Template = PyObject_GetAttrString(m, "Template");	// NEW REF
	if(!Template)
	{
		fprintf(stderr, "initcPeach(): Error: Template is null.\n");
	}

	Py_XDECREF(m);
}

// end
