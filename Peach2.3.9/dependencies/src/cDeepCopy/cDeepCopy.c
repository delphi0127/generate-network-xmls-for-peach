
// Native implementation of deepcopy from copy.py in Python v2.6
// Author: Michael Eddington (mike@phed.org)

#include <Python.h>
#define VERSION "0.1"
#define MODULE "cDeepCopy"

static PyObject *moduleError;
static PyObject *_copy_dispatch;
static PyObject *_deepcopy_dispatch;
static PyObject *_EmptyClass;
static PyObject *_version;
static PyObject *_dispatch_table;

static char *moduleDoc = "Native implementation of the DeepCopy in copy.py, based on Python v2.6 code.";

static PyObject* _deepcopy_atomic(PyObject* self, PyObject* args);
static PyObject* _deepcopy(PyObject* x, PyObject* memo);

static PyObject* _reconstruct(PyObject *x, PyObject *info, int deep, PyObject* memo)
{
	int		n;
	char*	err;
	PyObject *callable, *args, *state, *y=NULL, *tmp, *listiter, *dictiter, *slotstate;

	//if isinstance(info, str):
	if(PyString_Check(info))
	{
		//return x
		Py_XINCREF(x);	// INC
		return x;
	}

	//assert isinstance(info, tuple)
	if(!PyTuple_Check(info))
	{
		fprintf(stderr, "_reconstruct(): assert isinstance(info, tuple) failed\n");
		err = "__reduce__() not str or tuple!";
L0:		PyErr_SetString(PyExc_AssertionError,err);
		return NULL;
	}

	// if memo is None:
	if(!memo)
	{
		err = "memo is null!";
		goto L0;
	}

	//n = len(info)
	n = PyTuple_Size(info);
	//assert n in (2, 3, 4, 5)
	if(n < 2 || n > 5)
	{
		err = "len(__reduce__()) not in (2, 3, 4, 5)!";
		fprintf(stderr, "_reconstruct(): len(__reduce__()) not in (2, 3, 4, 5)!\n");
		goto L0;
	}

	//callable, args = info[:2]
	callable = PyTuple_GET_ITEM(info, 0);	// BORROWED REF
	args = PyTuple_GET_ITEM(info, 1);		// BORROWED REF
	//if n > 2:
	if(n > 2)
	{
		//state = info[2]
		state = PyTuple_GET_ITEM(info, 2);	// BORROWED REF
		Py_XINCREF(state);					// ADD REF
	}
	else
		//state = {}
		state = PyDict_New();				// NEW REF

	//if n > 3:
	if(n > 3)
	{
		//listiter = info[3]
		listiter = PyTuple_GET_ITEM(info, 3);	// BORROWED REF
	}
	else
		//listiter = None
		listiter = NULL;

	//if n > 4:
	if(n > 4)
		//dictiter = info[4]
		dictiter = PyTuple_GET_ITEM(info, 4);	// BORROWED REF
	else
		//dictiter = None
		dictiter = NULL;

	if(deep)
	{
		//args = deepcopy(args, memo)
		args = _deepcopy(args, memo);	// NEW REF
		if(!args || PyErr_Occurred())
		{
			err = "_reconstruct(): args = _deepcopy(args,memo);!";
			fprintf(stderr, "_reconstruct(): Error: args = _deepcopy(args,memo);\n");
			goto L0;
		}
	}

	//y = callable(*args)
	y = PyObject_CallObject(callable, args);	// NEW REF

	if(!y || PyErr_Occurred())
	{
		fprintf(stderr, "\n\n");
		PyErr_Print();
		fprintf(stderr, "\n\n");

		err = "_reconstruct(): y = PyObject_CallObject(callable, args); Failed";
		fprintf(stderr, "_reconstruct(): y = PyObject_CallObject(callable, args); Failed\n");
		fprintf(stderr, "_reconstruct(): callable = [%s], args = [%s]\n", PyString_AsString(PyObject_Repr(callable)),
			PyString_AsString(PyObject_Repr(args)));
		Py_XDECREF(y);
		y = NULL;
		goto L0;
	}

	//memo[id(x)] = y
	tmp = PyLong_FromVoidPtr(x);	// NEW REF
	PyDict_SetItem(memo, tmp, y);
	
	Py_XDECREF(tmp);	// DEC REF
	tmp = NULL;

	//if listiter is not None:
	if(listiter && PyObject_IsTrue(listiter))
	{
		PyObject* item;
		Py_ssize_t count;
		Py_ssize_t cnt = 0;

		//for item in listiter:
		count = PyList_GET_SIZE(listiter);
		for(cnt = 0; cnt < count; cnt++)
		{
			item = PyList_GetItem(listiter, cnt);	// BORROWED REF
			if(!item)
			{
				fprintf(stderr, "_reconstruct(): Bad things #1!\n");
				PyErr_Print();
			}
			//if deep:
			if(deep)
				item = _deepcopy(item, memo);	// NEW REF??
			
			//y.append(item)
			PyList_Append(y, item);
			
			if(deep)
			{
				Py_XDECREF(item);	// DEC REF ?
			}
		}
	}

	if(PyErr_Occurred())
	{
		fprintf(stderr, "_reconstruct(): Something in listiter failed\n");
	}

	if(dictiter && PyObject_IsTrue(dictiter))
	{
		PyObject* item;
		PyObject* key;
		PyObject* value;
		Py_ssize_t count;
		Py_ssize_t cnt = 0;

		//for key, value in dictiter:
		PyObject* items = PyDict_Items(dictiter);	// NEW REF
		count = PyList_GET_SIZE(items);
		for(cnt = 0; cnt < count; cnt++)
		{
			item = PyList_GetItem(items, cnt);	// BORROWED REF
			key = PyTuple_GET_ITEM(item, 0);	// BORROWED REF
			value = PyTuple_GET_ITEM(item, 1);	// BORROWED REF

			//if deep:
			if(deep)
			{
				//key = deepcopy(key, memo)
				key = _deepcopy(key, memo);	// NEW REF
				if(!key || PyErr_Occurred())
				{
					fprintf(stderr, "_reconstruct(): key = _deepcopy(key, memo); Failed\n");
				}

				//value = deepcopy(value, memo)
				value = _deepcopy(value, memo);	// NEW REF
				if(!value || PyErr_Occurred())
				{
					fprintf(stderr, "_reconstruct(): value = _deepcopy(value, memo); Failed\n");
				}
			}

			//y[key] = value
			PyDict_SetItem(y, key, value);

			if(deep)
			{
				Py_XDECREF(key);	// DEC REF
				Py_XDECREF(value);	// DEC REF
			}
		}

		Py_XDECREF(items);	// DEC REF
	}

	if(PyErr_Occurred())
	{
		fprintf(stderr, "_reconstruct(): Something in dictiter failed\n");
	}

	//if state:
	if(y && PyObject_IsTrue(state))
	{
		//if deep:
		if(deep)
		{
			//state = deepcopy(state, memo)
			state = _deepcopy(tmp=state, memo);	// NEW REF
			Py_XDECREF(tmp);

			if(!state || PyErr_Occurred())
			{
				fprintf(stderr, "_reconstruct(): state = _deepcopy(tmp=state, memo); Failed\n");
			}
		}

		//if hasattr(y, '__setstate__'):
		if(PyObject_HasAttrString(y, "__setstate__"))
		{
			PyObject* tmp2;
			//y.__setstate__(state)
			tmp = PyObject_GetAttrString(y, "__setstate__"); // NEW REF
			tmp2 = Py_BuildValue("(O)", state);	// NEW REF
			PyObject_CallObject(tmp, tmp2);

			Py_XDECREF(tmp);	// DEC REF
			Py_XDECREF(tmp2);	// DEC REF

			if(PyErr_Occurred())
			{
				fprintf(stderr, "_reconstruct(): Calling __setstate__ Failed\n");
			}
		}
		else
		{
			//if isinstance(state, tuple) and len(state) == 2:
			if(PyObject_IsInstance(state, (PyObject*) &PyTuple_Type) && PyTuple_Size(state) == 2)
			{
				//state, slotstate = state
				tmp = state;
				state = PyTuple_GET_ITEM(tmp, 0);		// BORROWED REF
				slotstate = PyTuple_GET_ITEM(tmp, 1);	// BORROWED REF

				Py_XDECREF(tmp);	// DEC REF
				Py_XINCREF(state);	// INC REF

				if(PyErr_Occurred())
				{
					fprintf(stderr, "_reconstruct(): Something in state failed 3\n");
				}
			}
			//else:
			else
			{
				if(PyErr_Occurred())
				{
					fprintf(stderr, "_reconstruct(): if(PyObject_IsInstance(state, (PyObject*) &PyTuple_Type) && PyTuple_Size(state) == 2) FAILED\n");
				}

				//slotstate = None
				slotstate = NULL;
			}

			if(state)
			{
				//y.__dict__.update(state)
				tmp = PyObject_GetAttrString(y, "__dict__");	// NEW REF
				if(!tmp || PyErr_Occurred())
				{
					fprintf(stderr, "_reconstruct(): tmp = PyObject_GetAttrString(y, \"__dict__\"); Failed\n");
					fprintf(stderr, "_reconstruct(): y = [%s]\n", PyString_AsString(PyObject_Repr(y)));
				}

				PyDict_Update(tmp, state);
				
				Py_XDECREF(tmp);	// DEC REF
			}

			//if slotstate is not None:
			if(slotstate)
			{
				PyObject* item;
				PyObject* key;
				PyObject* value;
				Py_ssize_t count;
				Py_ssize_t cnt = 0;

				//for key, value in slotstate.iteritems():
				PyObject* items = PyDict_Items(slotstate);	// NEW REF
				count = PyList_GET_SIZE(items);
				for(cnt = 0; cnt < count; cnt++)
				{
					item = PyList_GetItem(items, cnt);	// BORROWED REF
					key = PyTuple_GET_ITEM(item, 0);	// BORROWED REF
					value = PyTuple_GET_ITEM(item, 1);	// BORROWED REF

					//setattr(y, key, value)
					PyObject_SetAttr(y, key, value);
				}

				Py_XDECREF(items);	// DEC REF

				if(PyErr_Occurred())
				{
					fprintf(stderr, "_reconstruct(): Something in state failed 1\n");
				}

			}

		}
	}


	// This will need to change?
L1:	if(deep)
	{
		Py_XDECREF(args);
	}

	Py_XDECREF(state);

	if(PyErr_Occurred())
	{
		fprintf(stderr, "_reconstruct(): PyErr_Occurred\n");
		Py_XDECREF(y);
		y = NULL;
	}
	else if(!y)
	{
		fprintf(stderr, "_reconstruct(): Why is y null!?\n");
	}

	return y;
}

static int cnt = 0;

#define ENTER() cnt++;
#define EXIT() cnt--;
//#define MSG(msg) fprintf(stderr, "[%d] %s\n", cnt, msg)
#define MSG(msg)

/*the internal part of deepcopy*/
static PyObject* _deepcopy(PyObject* x, PyObject* memo)
{
	PyObject	*t = NULL, 
		*c = NULL, 
		*y = NULL,
		*cls = NULL,
		*copier = NULL,
		*reductor = NULL,
		*rv = NULL;

	//fprintf(stderr, "_deepcopy(): %s\n", PyString_AsString(PyObject_Repr(x)));

	// if memo is None:
	if(!memo || !PyDict_Check(memo))
	{
		// memo = {}
		memo = PyDict_New();	// NEW REF
	}
	else
	{
		Py_INCREF(memo);	// INC REF (balances NEW REF)

		// d = id(x)
		c = PyLong_FromVoidPtr(x);	// NEW REF
		// y = memo.get(d, _nil)
		y = PyDict_GetItem(memo, c);	// BORROWED REF

		Py_XDECREF(c);	// DEC REF
		c = NULL;

		// if y is not _nil:
		if(y && y != Py_None)
		{
			// return y
			Py_XINCREF(y);	// INC REF
			goto L_exit;
		}
	}

	// cls = type(x)
	cls = PyObject_Type(x);	// NEW REF

	// copier = _deepcopy_dispatch.get(cls)
	copier = cls ? PyDict_GetItem(_deepcopy_dispatch, cls) : NULL;	// BORROWED REF
	t = NULL;

	// if copier:
	if(copier)
	{
		// y = copier(x, memo)
		if(PyErr_Occurred())
		{
			fprintf(stderr, "_deepcopy(): copier(x, memo) failed\n");
			goto L_exit;
		}

		t = Py_BuildValue("(OO)", x, memo);	// NEW REF
		if(PyErr_Occurred())
		{
			fprintf(stderr, "_deepcopy(): Py_BuildValue(\"(OO)\", x, memo); failed\n");
			goto L_exit;
		}
		
		PyErr_Clear();
		y = PyObject_CallObject(copier, t);	// NEW REF
		if(!y)
		{
			fprintf(stderr, "_deepcopy(): (1) y = PyObject_CallObject(copier, t); failed\n");
			fprintf(stderr, "_deepcopy(): (1) x[%s] cls[%s] copier[%s]\n", 
				PyString_AsString(PyObject_Repr(x)), 
				PyString_AsString(PyObject_Repr(cls)), 
				PyString_AsString(PyObject_Repr(copier)));
			PyErr_Print();
			fprintf(stderr, "\n");

			Py_XDECREF(t);	// DEC REF
			goto L_exit;
		}

		Py_XDECREF(t);	// DEC REF
	}
	else
	{
		//y = checkCopyAttr(x,t,"__deepcopy__","deep",memo);
		PyObject	*info;
		char		buf[512];

		PyErr_Clear();

		// issc = issubclass(cls, type)
		if(PyObject_IsSubclass(cls, (PyObject*) &PyType_Type) && 
			!(PyErr_Occurred() && PyErr_ExceptionMatches(PyExc_TypeError)) )
		{
			// y = _deepcopy_atomic(x, memo)
			y = _deepcopy_atomic(x, memo);	// NEW
			if(!y)
				fprintf(stderr, "_deepcopy(): y = _deepcopy_atomic(x, memo); failed\n");
		}
		else
		{
			if(PyObject_HasAttrString(x, "__deepcopy__dont_use__") == 0 && PyObject_HasAttrString(x, "__deepcopy__") == 1)
			{
				// y = copier(memo)
				copier = PyObject_GetAttrString(x, "__deepcopy__");	// NEW REF
				if(PyErr_Occurred())
				{
					fprintf(stderr, "_deepcopy(): copier = PyObject_GetAttrString(x, \"__deepcopy__\") failed\n");
					Py_XDECREF(copier);
					goto L_exit;
				}

				t = Py_BuildValue("(O)", memo);	// NEW REF
				if(PyErr_Occurred())
				{
					fprintf(stderr, "_deepcopy(): t = Py_BuildValue(\"(O)\", memo); failed\n");
					Py_XDECREF(copier);
					goto L_exit;
				}

				y = PyObject_CallObject(copier, t);	// NEW REF
				if(!y)
				{
					fprintf(stderr, "_deepcopy(): (2) y = PyObject_CallObject(copier, t); failed\n");
					PyErr_Print();
					fprintf(stderr, "\n");

					Py_XDECREF(t);		// DEC REF
					Py_XDECREF(copier);	// DEC REF
					goto L_exit;
				}

				Py_XDECREF(t);		// DEC REF
				Py_XDECREF(copier);	// DEC REF
			}
			else
			{
				PyErr_Clear();

				//reductor = dispatch_table.get(cls)
				reductor = PyDict_GetItem(_dispatch_table, cls);	// BORROWED REF
				//if reductor:
				if(reductor)
				{
					//rv = reductor(x)
					if(PyErr_Occurred())
					{
						fprintf(stderr, "_deepcopy(): reductor = PyDict_GetItem(_dispatch_table, cls); failed\n");
						goto L_exit;
					}

					t = Py_BuildValue("(O)", x);	// NEW REF
					if(PyErr_Occurred())
					{
						fprintf(stderr, "_deepcopy(): t = Py_BuildValue(\"(O)\", x); failed\n");
						goto L_exit;
					}

					rv = PyObject_CallObject(reductor, t);	// NEW REF
					Py_XDECREF(t);
				}
				//else:
				else
				{
					//reductor = getattr(x, "__reduce_ex__", None)
					//if reductor:
					if(PyObject_HasAttrString(x,"__reduce_ex__"))	// NEW REF
					{
						//rv = reductor(2)
						reductor = PyObject_GetAttrString(x,"__reduce_ex__");
						if(PyErr_Occurred())
						{
							fprintf(stderr, "_deepcopy(): reductor = PyObject_GetAttrString(x,\"__reduce_ex__\") failed\n");
							Py_XDECREF(reductor);
							goto L_exit;
						}

						t = Py_BuildValue("(i)", 2);	// NEW REF
						if(PyErr_Occurred())
						{
							fprintf(stderr, "_deepcopy(): t = Py_BuildValue(\"(i)\", 2); failed\n");
							Py_XDECREF(reductor);
							goto L_exit;
						}

						rv = PyObject_CallObject(reductor, t);	// NEW REF
						Py_XDECREF(reductor);
						Py_XDECREF(t);
					}
					//else:
					else
					{
						PyErr_Clear();

						//reductor = getattr(x, "__reduce__", None)
						//if reductor:
						if(PyObject_HasAttrString(x,"__reduce__"))	// NEW REF
						{
							//fprintf(stderr, "Building using __reduce__ [%s][%s]\n", PyString_AsString(PyObject_Repr(x)),PyString_AsString(PyObject_Repr(cls)));
							//rv = reductor()
							reductor = PyObject_GetAttrString(x,"__reduce__");
							if(PyErr_Occurred())
							{
								fprintf(stderr, "_deepcopy(): reductor = PyObject_GetAttrString(x,\"__reduce__\") failed\n");
								Py_XDECREF(reductor);
								goto L_exit;
							}

							rv = PyObject_CallObject(reductor, NULL);	// NEW REF
							Py_XDECREF(reductor);	// DEC REF
						}
						//else:
						else
						{
							//raise Error(
							//"un(deep)copyable object of type %s" % cls)
							char *fmt= "un(deep)copyable object of type %s";
							PyObject *ts = PyObject_Str(cls);
							char *tn = PyString_AsString(ts);
							int len = strlen(fmt) + strlen(tn);
							char *p = len < 512 ? buf : malloc(len+1);

							sprintf(p, fmt, tn);
							fprintf(stderr, "_deepcopy(): Error: %s\n", p);

							PyErr_Clear();
							PyErr_SetString(moduleError, p);
							
							if(p!=buf)
								free(p);
							
							//Py_DECREF(ts);

							y = NULL;
							goto L_exit;
						}
					}
				}

				//y = _reconstruct(x, rv, 1, memo)
				y = _reconstruct(x, rv, 1, memo);
				Py_XDECREF(rv);	// DEC REF

				if(PyErr_Occurred())
				{
					fprintf(stderr, "_deepcopy(): _reconstruct pyerr_occured\n");
					Py_XDECREF(y);
					y = NULL;
				}
				else if(!y)
					fprintf(stderr, "_deepcopy(): _reconstruct returned NULL y!\n");
			}
		}
	}

L_exit:
	Py_XDECREF(cls);	// DEC REF
	Py_XDECREF(memo);	// DEC REF

	if(PyErr_Occurred())
	{
		Py_XDECREF(y);
		y = NULL;

		fprintf(stderr, "_deepcopy(%s): PyErr_Occured()\n", PyString_AsString(PyObject_Repr(x)));
	}

	if(!y)
		fprintf(stderr, "_deepcopy(): y is NULL\n");

	return y;
}

static int InDeepCopy = 0;

static PyObject* deepcopy(PyObject* self, PyObject* args)
{
	PyObject	*x, *memo=NULL;
	PyObject* ret;

	//if(InDeepCopy++)
	//{
	//	fprintf(stderr, "\n\n------- Recursing -------------------\n\n");
	//}
	//else
	//{
	//	fprintf(stderr, "\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n");
	//	InDeepCopy = 1;
	//}

	ret = PyArg_ParseTuple(args, "O|O!:deepcopy", &x, &PyDict_Type, &memo) ? _deepcopy(x,memo) : NULL;

	//if(--InDeepCopy)
	//{
	//	fprintf(stderr, "\n\n------- Exit Recursing -----------------\n\n");
	//}
	//else
	//{
	//	fprintf(stderr, "\n\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n\n");
	//}

	return ret;
}

static PyObject* _deepcopy_atomic(PyObject* self, PyObject* args)
{
	PyObject*	x, *memo;
	if (!PyArg_ParseTuple(args, "OO!:_deepcopy_atomic", &x, &PyDict_Type, &memo)) return NULL;
	
	Py_INCREF(x);
	return x;
}

static	void _setMemo(PyObject* memo, PyObject *x, PyObject* y)
{
	PyObject *c = PyLong_FromVoidPtr(x);	// NEW REF c
	PyDict_SetItem(memo,c,y);
	Py_XDECREF(c);	// DEC REF c

	if(PyErr_Occurred())
	{
		fprintf(stderr, "_setMemo(): Detected error!\n");
	}
}

static PyObject* _deepcopy_dict(PyObject* self, PyObject* args)
{
	PyObject	*x, *memo, *y, *d, *e, *K, *Ki, *item;
	int			i, n;
	if (!PyArg_ParseTuple(args,"O!O!:_deepcopy_dict", &PyDict_Type, &x, &PyDict_Type, &memo)) return NULL;

	y = PyDict_New();	// NEW REF
	_setMemo(memo, x, y);

	K = PyDict_Keys(x);	// NEW REF
	n = PyList_Size(K);
	for(i=0; i<n; i++)
	{
		Ki = PyList_GetItem(K, i);	// BORROWED REF
		if(PyErr_Occurred())
		{
			fprintf(stderr, "_deepcopy_dict(): PyDict_GetItem error?\n");
			break;
		}

		d = _deepcopy(Ki, memo);	// NEW REF
		if(!d)
		{
			fprintf(stderr, "_deepcopy_dict(): Error _deepcopy(Ki, memo)\n");
			return NULL;
			//break;
		}
		if(PyErr_Occurred())
		{
			fprintf(stderr, "_deepcopy_dict(): _deepcopy(Ki, memo) error?\n");
			break;
		}

		item = PyDict_GetItem(x, Ki);	// BORROWED REF
		if(!item)
		{
			fprintf(stderr, "_deepcopy_dict(): Error, item was NULL\n");
			return NULL;
		}
		if(PyErr_Occurred())
		{
			fprintf(stderr, "_deepcopy_dict(): PyDict_GetItem(x,Ki) error?\n");
			break;
		}

		e = _deepcopy(item, memo);	// NEW REF
		if(!e)
		{ 
			fprintf(stderr, "_deepcopy_dict(): Error _deepcopy(item, memo)\n");
			return NULL;
			//break;
		}
		
		PyDict_SetItem(y, d, e);
		
		if(PyErr_Occurred())
		{
			fprintf(stderr, "_deepcopy_dict(): PyDict_SetItem error?\n");
			fprintf(stderr, "[%s]\n", PyString_AsString(PyObject_Repr(Ki)));
			fprintf(stderr, "[%s]\n", PyString_AsString(PyObject_Repr(d)));
			break;
		}

		Py_XDECREF(d);	// DEC REF
		Py_XDECREF(e);	// DEC REF
	}

	Py_XDECREF(K);	// DEC REF

	if(PyErr_Occurred())
	{
		fprintf(stderr, "_deepcopy_dict(): Detected error, returning null Y\n");
		Py_XDECREF(y);	// DEC REF
		y = NULL;
	}

	if(y == NULL)
		fprintf(stderr, "_deepcopy_dict(): Returning null y!\n");

	return y;
}

static PyObject* _deepcopy_list(PyObject* self, PyObject* args)
{
	PyObject	*x, *memo, *y, *d, *a, *tmp;
	Py_ssize_t	i, n;

	if (!PyArg_ParseTuple(args, "O!O!:_deepcopy_list", &PyList_Type, &x, &PyDict_Type, &memo)) return NULL;

	//y = []
	y = PyList_New(0);	// NEW REF
	n = PyList_Size(x);

	//memo[id(x)] = y
	_setMemo(memo, x, y);

	//for a in x:
	for(i=0; i<n; i++)
	{
		//y.append(deepcopy(a, memo))
		d = _deepcopy( PyList_GetItem(x, i), memo);	// NEW REF
		//if(!d) break; // should this be an error!?
		if(!d)
		{
			fprintf(stderr, "_deepcopy_list(): _deepcopy returned NULL\n");
			fprintf(stderr, "_deepcopy_list(): Returning null y! 3\n");
			Py_XDECREF(y);	// DEC REF
			return NULL;
		}
		else if(PyErr_Occurred())
		{
			fprintf(stderr, "_deepcopy_list(): _deepcopy PyErr_Occurred copying %s\n", PyString_AsString(PyObject_Repr(PyList_GetItem(x, i))));
			fprintf(stderr, "_deepcopy_list(): Returning null y! 4\n");
			Py_XDECREF(y);	// DEC REF
			return NULL;
		}

		PyList_Append(y, d);
		Py_XDECREF(d);	// DEC REF
	}

	if(PyErr_Occurred())
	{
		Py_XDECREF(y);	// DEC REF
		fprintf(stderr, "_deepcopy_list(): Returning null y! 1\n");
		return NULL;
	}

	if(y == NULL)
		fprintf(stderr, "_deepcopy_list(): Returning null y! 2\n");

	return y;
}

static PyObject* _deepcopy_tuple(PyObject* self, PyObject* args)
{
	PyObject	*x, *memo, *y, *d, *r, *xi, *yi;
	Py_ssize_t	i, n;

	if (!PyArg_ParseTuple(args, "O!O!:_deepcopy_tuple", &PyTuple_Type, &x, &PyDict_Type, &memo)) return NULL;

	y = PyList_New(0);	// NEW REF
	n = PyTuple_Size(x);

	for(i = 0; i < n; i++)
	{
		d = _deepcopy(PyTuple_GetItem(x, i), memo);	// BORROWED REF, NEW REF
		if(!d)
		{
			// We shouldn't get here!
			fprintf(stderr, "_deepcopy_tuple(): Very bad things occured #1\n");
			//Py_DECREF(y);
			return NULL;
		}

		PyList_Append(y, d);
		Py_DECREF(d);	// DEC REF
	}

	d = PyLong_FromVoidPtr(x);	// NEW REF
	r = PyDict_GetItem(memo, d);	// BORROWED REF
	Py_XDECREF(d);

	if(r)
	{
		Py_XINCREF(r);
		Py_XDECREF(y);
		return r;
	}

	r = x;
	Py_XINCREF(r);	// INC REF

	for(i=0; i < n; i++)
	{
		xi = PyTuple_GetItem(r, i);	// BORROWED REF
		yi = PyList_GetItem(y, i);	// BORROWED REF
		if(!xi || !yi)
		{
			Py_XDECREF(r);	// DEC REF
			Py_XDECREF(y);	// DEC REF

			fprintf(stderr, "_deepcopy_tuple(): Very bad things occured #2 (%d:%d)\n", i, n);
			if(!xi)
				fprintf(stderr, "_deepcopy_tuple(): xi is null.\n");
			if(!yi)
				fprintf(stderr, "_deepcopy_tuple(): yi is null.\n");
			 
			return NULL;
		}
		else if(xi != yi)
		{
			Py_XDECREF(r); // DEC REF
			r = PyList_AsTuple(y);	// NEW REF
			break;
		}
	}

	Py_XDECREF(y);	// DEC REF
	
	_setMemo(memo, x, r);
	
	if(r == NULL)
		fprintf(stderr, "_deepcopy_tuple(): Returning null r!\n");

	return r;
}

static	int __keep_alive(PyObject *x, PyObject *memo)
{
	int			r = -1;
	PyObject	*c = PyLong_FromVoidPtr(x);		// NEW REF
	PyObject	*t = PyDict_GetItem(memo, c);	// BORROWED REF
	PyObject	*tmp;

	if(!t)
	{
		if(!PyErr_ExceptionMatches(PyExc_KeyError)) goto L_exit;
		PyDict_SetItem(memo, c, tmp = Py_BuildValue("[O]", x));	// NEW REF
		Py_XDECREF(tmp);	// DEC REF
	}

	r = 0;

L_exit:
	Py_XDECREF(c);	// DEC REF
	return r;
}

static PyObject* _deepcopy_inst(PyObject* self, PyObject* args)
{
	PyObject	*x, *a=NULL, *klass=NULL, *y=NULL, *state=NULL, *r=NULL, *memo;

	if (!PyArg_ParseTuple(args, "O!O!:_deepcopy_inst", &PyInstance_Type, &x, &PyDict_Type, &memo)) return NULL;
	
	if(PyObject_HasAttrString(x, "__deepcopy__dont_use__") == 0 && PyObject_HasAttrString(x, "__deepcopy__") == 1)
		return PyObject_CallMethod(x, "__deepcopy__", "O", memo);	// NEW REF

	if (PyObject_HasAttrString(x, "__getinitargs__"))
	{
		//fprintf(stderr, "Building using __getinitargs__\n");
		//args = x.__getinitargs__()
		y = PyObject_CallMethod(x, "__getinitargs__", NULL);	// NEW REF
		
		//args = deepcopy(args, memo)
		//y = x.__class__(*args)
		if (!y || !PyObject_HasAttrString(x, "__class__"))
		{
			if(!y)
			{
				fprintf(stderr, "_deepcopy_inst(): Error: y is NULL\n");
				PyErr_SetString(PyExc_Exception, "_deepcopy_inst(): Error: y is NULL");
			}
			else
			{
				fprintf(stderr, "_deepcopy_inst(): Error: klass is NULL\n");
				PyErr_SetString(PyExc_Exception, "_deepcopy_inst(): Error: klass is NULL");
			}

			return NULL;
		}

		klass = PyObject_GetAttrString(x, "__class__");	// NEW REF
		__keep_alive(y, memo);
		a = _deepcopy(y, memo);	// NEW REF

		Py_XDECREF(y);	// DEC REF
		y = NULL;
		
		if(!a)
		{
			fprintf(stderr, "_deepcopy_inst(): Error: a is NULL\n");
			PyErr_SetString(PyExc_Exception, "_deepcopy_inst(): Error: a is NULL");
			goto L_exit;
		}
		
		y = PyObject_CallObject(klass, a);	// NEW REF
		if(!y)
		{
			fprintf(stderr, "_deepcopy_inst(): Error: y is NULL\n");
			PyErr_SetString(PyExc_Exception, "_deepcopy_inst(): Error: y is NULL");
			goto L_exit;
		}

		Py_XDECREF(a);	// DEC REF
		a = NULL;
		Py_XDECREF(klass);
		klass = NULL;
	}
	else
	{
		//fprintf(stderr, "Building using _EmptyClass\n");
		//y = _EmptyClass()
		y = PyInstance_New(_EmptyClass, NULL, NULL);	// NEW REF
		if(!y)
		{
			fprintf(stderr, "_deepcopy_inst(): Unable to create instance of _EmptyClass\n");
			PyErr_SetString(PyExc_Exception, "_deepcopy_inst(): Unable to create instance of _EmptyClass");
			goto L_exit;
		}

		//y.__class__ = x.__class__
		klass = PyObject_GetAttrString(x, "__class__");	// NEW REF
		if(!klass)
		{
			fprintf(stderr, "_deepcopy_inst(): Unable to get attribute __class__ from x\n");
			PyErr_SetString(PyExc_Exception, "_deepcopy_inst(): Unable to get attribute __class__ from x");
			return NULL;
		}
		
		PyObject_SetAttrString(y, "__class__", klass);

		Py_XDECREF(klass);
		klass = NULL;
	}

	_setMemo(memo, x, y);
	
	if (PyObject_HasAttrString(x,"__getstate__"))
	{
		a = PyObject_CallMethod(x, "__getstate__", NULL);	// NEW REF
		__keep_alive(a, memo);
	}
	else
	{
		a = PyObject_GetAttrString(x, "__dict__");	// NEW REF
	}
	
	if(!a)
	{
		fprintf(stderr, "_deepcopy_inst(): Object a is NULL\n");
		PyErr_SetString(PyExc_Exception, "_deepcopy_inst(): Object a is NULL\n");
		goto L_exit;
	}
	
	state = _deepcopy(a, memo); // NEW
	if(!state && !PyErr_Occurred())
	{
		fprintf(stderr, "_deepcopy_inst(): Failed to _deepcopy state\n");
		PyErr_SetString(PyExc_Exception, "_deepcopy_inst(): Failed to _deepcopy state\n");
		goto L_exit;
	}
	else if(PyErr_Occurred())
	{
		fprintf(stderr, "_deepcopy_inst(): Failed to _deepcopy state, got error\n");
		goto L_exit;
	}

	Py_XDECREF(a);
	a = NULL;

	if (PyObject_HasAttrString(y,"__setstate__"))
	{
		PyObject_CallMethod(y, "__setstate__", "O", state);
	}
	else
	{
		PyObject *d = PyObject_GetAttrString(y, "__dict__");	// NEW REF
		if(!d)
		{
			fprintf(stderr, "_deepcopy_inst(): Unable to get attribute __dict__ from object y\n");
			PyErr_SetString(PyExc_Exception, "_deepcopy_inst(): Unable to get attribute __dict__ from object y");
			goto L_exit;
		}

		if(!PyDict_Check(d) || PyDict_Update(d, state))
		{
			fprintf(stderr, "_deepcopy_inst(): Error updating __dict__!\n");
			if(!PyErr_Occurred())
				PyErr_SetString(PyExc_Exception, "_deepcopy_inst(): Error updating __dict__!");
			
			//Py_XDECREF(d);
			goto L_exit;
		}

		Py_XDECREF(d);	// DEC REF
	}

	if(!PyErr_Occurred())
	{
		r = y;
		y = NULL;
	}
	else
	{
		fprintf(stderr, "_deepcopy_inst(): Detected error, exiting\n");
		//PyErr_Print();
	}

L_exit:
	Py_XDECREF(state);
	Py_XDECREF(y);

	if(r == NULL && !PyErr_Occurred())
	{
		fprintf(stderr, "_deepcopy_inst(): Returning null r!\n");
		PyErr_SetString(PyExc_Exception, "_deepcopy_inst(): Error: klass is NULL");
	}

	return r;
}

static struct PyMethodDef moduleMethods[] = {
	{"deepcopy",			deepcopy,			METH_VARARGS, "Deep copy operation on arbitrary Python objects.\n\n"
	"See the module's __doc__ string for more info."},
	{"_deepcopy_atomic",	_deepcopy_atomic,	METH_VARARGS, "Deep copy atomic argument"},
	{"_deepcopy_dict",		_deepcopy_dict,		METH_VARARGS, "Deep copy dictionary argument"},
	{"_deepcopy_inst",		_deepcopy_inst,		METH_VARARGS, "Deep copy instance argument"},
	{"_deepcopy_list",		_deepcopy_list,		METH_VARARGS, "Deep copy list argument"},
	{"_deepcopy_tuple",		_deepcopy_tuple,	METH_VARARGS, "Deep copy tuple argument"},
	{NULL,	NULL}			/*sentinel*/
};

void initcDeepCopy()
{
	PyObject *m, *d, *t, *_t, *u, *v, *k;
	static	struct {char* tn; int which;} atomics[]={
		{"NoneType",3},
		{"IntType",3},
		{"LongType",3},
		{"FloatType",3},
		{"ComplexType",3},
		{"StringType",3},
		{"UnicodeType",3},
		{"CodeType",3},
		{"TypeType",3},
		{"XRangeType",3},
		{"ClassType",1},
		{NULL,0}}, *sa;
		static	char *specials[]={
			"ListType", "_copy_list", "_deepcopy_list",
			"TupleType", "_copy_tuple", "_deepcopy_tuple",
			"DictionaryType", "_copy_dict", "_deepcopy_dict",
			"InstanceType", "_copy_inst", "_deepcopy_inst",
			NULL
		};

		char	**a;

		/* Create the module and add the functions */
		m = Py_InitModule(MODULE, moduleMethods);

		_dispatch_table = PyDict_GetItemString(
			PyModule_GetDict(PyImport_ImportModule("copy_reg")),
			"dispatch_table");

		/* Add some symbolic constants to the module */
		d = PyModule_GetDict(m);
		_version = PyString_FromString(VERSION);
		PyDict_SetItemString(d, "_version", _version );
		moduleError = PyErr_NewException(MODULE ".Error",NULL,NULL);
		PyDict_SetItemString(d, "Error", moduleError);
		PyDict_SetItemString(d,"error",moduleError);

		v = PyDict_New();
		PyDict_SetItemString(v, "__module__", t=PyString_FromString(MODULE));
		_EmptyClass = PyClass_New(NULL,v,_t=PyString_FromString("_EmptyClass"));
		PyDict_SetItemString(d, "_EmptyClass", _EmptyClass);
		//Py_XDECREF(v);
		//Py_XDECREF(_t);
		//Py_XDECREF(t);

		PyDict_SetItemString(d, "_deepcopy_dispatch", _deepcopy_dispatch = PyDict_New());
		_t = PyImport_ImportModule("types");
		t = PyModule_GetDict(_t);
		u = PyDict_GetItemString(d,"_deepcopy_atomic");	/*borrowed*/
		for(sa=atomics;sa->tn;sa++){
			k = PyDict_GetItemString(t,sa->tn);	/*borrowed*/
			if((sa->which&2) && k && PyDict_SetItem(_deepcopy_dispatch,k,u)){
				//Py_DECREF(k);
				//Py_DECREF(u);
			}
		}
		for(a=specials;*a;a+=3){
			k = PyDict_GetItemString(t,*a);	/*borrowed*/
			v = PyDict_GetItemString(d,a[2]);
			if(k && PyDict_SetItem(_deepcopy_dispatch,k,v)){
				//Py_DECREF(k);
				//Py_DECREF(v);
			}
		}

		/*add in the docstring*/
		v = Py_BuildValue("s", moduleDoc);
		PyDict_SetItemString(d, "__doc__", v);
		//Py_DECREF(v);
		//Py_DECREF(_t);
}

// end
