<?xml version='1.0'?>
<fragment>
<production name="1">
  <non-terminal>locationPath</non-terminal>
  <rule>
    <symbol>relativeLocationPath</symbol>
  </rule>
  <rule>
    <symbol>absoluteLocationPath</symbol>
  </rule>
</production>

<production name="2">
  <non-terminal>absoluteLocationPath</non-terminal>
  <rule>
    <symbol>'/'</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedAbsoluteLocationPath, "O", Py_None);
    </code>
    <code language="python">
      $$ = ParsedAbsoluteLocationPath(None)
    </code>
  </rule>
  <rule>
    <symbol>'/'</symbol>
    <symbol>relativeLocationPath</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedAbsoluteLocationPath, "O", $2);
    </code>
    <code language="python">
      $$ = ParsedAbsoluteLocationPath($2)
    </code>
  </rule>
  <rule>
    <symbol>abbreviatedAbsoluteLocationPath</symbol>
  </rule>
</production>

<production name="3">
  <non-terminal>relativeLocationPath</non-terminal>
  <rule>
    <symbol>step</symbol>
  </rule>
  <rule>
    <symbol>relativeLocationPath</symbol>
    <symbol>'/'</symbol>
    <symbol>step</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedRelativeLocationPath, "OO", $1, $3);
    </code>
    <code language="python">
      $$ = ParsedRelativeLocationPath($1, $3)
    </code>
  </rule>
  <rule>
    <symbol>abbreviatedRelativeLocationPath</symbol>
  </rule>
</production>

<production name="4">
  <non-terminal>step</non-terminal>
  <rule>
    <symbol>axisSpecifier</symbol>
    <symbol>nodeTest</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedStep, "OO", $1, $2);
    </code>
    <code language="python">
      $$ = ParsedStep($1, $2)
    </code>
  </rule>
  <rule>
    <symbol>axisSpecifier</symbol>
    <symbol>nodeTest</symbol>
    <symbol>predicateList</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedStep, "OOO", $1, $2, $3);
    </code>
    <code language="python">
      $$ = ParsedStep($1, $2, $3)
    </code>
  </rule>
  <rule>
    <symbol>abbreviatedStep</symbol>
  </rule>
</production>

<production name="4a">
  <non-terminal>predicateList</non-terminal>
  <rule>
    <symbol>predicate</symbol>
    <code language="c">
      PyObject *pred_list = PyList_New(1);
      /* Steals a reference */
      PyList_SET_ITEM(pred_list, 0, $1);
      Py_INCREF($1);
      $$ = PyObject_CallFunction(ParsedPredicateList, "O", pred_list);
      Py_DECREF(pred_list);
    </code>
    <code language="python">
      $$ = ParsedPredicateList([$1])
    </code>
  </rule>
  <rule>
    <symbol>predicateList</symbol>
    <symbol>predicate</symbol>
    <code language="c">
      PyObject_CallMethod($1, "append", "O", $2);
      Py_INCREF($1);
      $$ = $1;
    </code>
    <code language="python">
      $1.append($2)
      $$ = $1
    </code>
  </rule>
</production>

<production name="5">
  <non-terminal>axisSpecifier</non-terminal>
  <rule>
    <symbol>AXIS_NAME</symbol>
    <symbol>DOUBLE_COLON</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedAxisSpecifier, "O", $1);
    </code>
    <code language="python">
      $$ = ParsedAxisSpecifier($1)
    </code>
  </rule>
  <rule>
    <symbol>abbreviatedAxisSpecifier</symbol>
  </rule>
</production>

<!--
<production name="6">
  <non-terminal>axisName</non-terminal>
  <rule>
    <symbol>AXIS_NAME</symbol>
  </rule>
  <code language="python">
  </code>
</production>
-->

<production name="7">
  <non-terminal>nodeTest</non-terminal>
  <rule>
    <symbol>WILDCARD_NAME</symbol>
    <code language="C">
      $$ = PyObject_CallFunction(ParsedNameTest, "O", $1);
    </code>
    <code language="python">
      $$ = ParsedNameTest($1)
    </code>
  </rule>
  <rule>
    <symbol>NODE_TYPE</symbol>
    <symbol>'('</symbol>
    <symbol>')'</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedNodeTest, "O", $1);
    </code>
    <code language="python">
      $$ = ParsedNodeTest($1)
    </code>
  </rule>
  <rule>
    <symbol>NODE_TYPE</symbol>
    <symbol>'('</symbol>
    <symbol>LITERAL</symbol>
    <symbol>')'</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedNodeTest, "OO", $1, $3);
    </code>
    <code language="python">
      $$ = ParsedNodeTest($1, $3)
    </code>
  </rule>
</production>

<production name="8">
  <non-terminal>predicate</non-terminal>
  <rule>
    <symbol>'['</symbol>
    <symbol>predicateExpr</symbol>
    <symbol>']'</symbol>
    <code language="c">
      Py_INCREF($2);
      $$ = $2;
    </code>
    <code language="python">
      $$ = $2
    </code>
  </rule>
</production>

<production name="9">
  <non-terminal>predicateExpr</non-terminal>
  <rule>
    <symbol>expr</symbol>
  </rule>
</production>

<production name="10">
  <non-terminal>abbreviatedAbsoluteLocationPath</non-terminal>
  <rule>
    <symbol>DOUBLE_SLASH</symbol>
    <symbol>relativeLocationPath</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedAbbreviatedAbsoluteLocationPath,
                                 "O", $2);
    </code>
    <code language="python">
      $$ = ParsedAbbreviatedAbsoluteLocationPath($2)
    </code>
  </rule>
</production>

<production name="11">
  <non-terminal>abbreviatedRelativeLocationPath</non-terminal>
  <rule>
    <symbol>relativeLocationPath</symbol>
    <symbol>DOUBLE_SLASH</symbol>
    <symbol>step</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedAbbreviatedRelativeLocationPath,
                                 "OO", $1, $3);
    </code>
    <code language="python">
      $$ = ParsedAbbreviatedRelativeLocationPath($1, $3)
    </code>
  </rule>
</production>

<production name="12">
  <non-terminal>abbreviatedStep</non-terminal>
  <rule>
    <symbol>'.'</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedAbbreviatedStep, "i", 0);
    </code>
    <code language="python">
      $$ = ParsedAbbreviatedStep(0)
    </code>
  </rule>
  <rule>
    <symbol>DOUBLE_DOT</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedAbbreviatedStep, "i", 1);
    </code>
    <code language="python">
      $$ = ParsedAbbreviatedStep(1)
    </code>
  </rule>
</production>

<production name="13">
  <non-terminal>abbreviatedAxisSpecifier</non-terminal>
  <rule>
    <symbol>'@'</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedAxisSpecifier, "s", "attribute");
    </code>
    <code language="python">
      $$ = ParsedAxisSpecifier("attribute")
    </code>
  </rule>
  <rule>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedAxisSpecifier, "s", "child");
    </code>
    <code language="python">
      $$ = ParsedAxisSpecifier("child")
    </code>
  </rule>
</production>

<production name="14">
  <non-terminal>expr</non-terminal>
  <!-- Bypass -->
  <rule>
    <symbol>orExpr</symbol>
  </rule>
</production>

<production name="15">
  <non-terminal>primaryExpr</non-terminal>
  <rule>
    <symbol>VARIABLE_REFERENCE</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedVariableReferenceExpr, "O", $1);
    </code>
    <code language="python">
      $$ = ParsedVariableReferenceExpr($1)
    </code>
  </rule>
  <rule>
    <symbol>'('</symbol>
    <symbol>expr</symbol>
    <symbol>')'</symbol>
    <code language="c">
      $$ = $2;
      Py_INCREF($2);
    </code>
    <code language="python">
      $$ = $2
    </code>
  </rule>
  <rule>
    <symbol>LITERAL</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedLiteralExpr, "O", $1);
    </code>
    <code language="python">
      $$ = ParsedLiteralExpr($1)
    </code>
  </rule>
  <rule>
    <symbol>NLITERAL</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedNLiteralExpr, "O", $1);
    </code>
    <code language="python">
      $$ = ParsedNLiteralExpr($1)
    </code>
  </rule>
  <!-- Bypass -->
  <rule>
    <symbol>functionCall</symbol>
  </rule>
</production>

<production name="16">
  <non-terminal>functionCall</non-terminal>
  <rule>
    <symbol>FUNCTION_NAME</symbol>
    <symbol>'('</symbol>
    <symbol>')'</symbol>
    <code language="c">
      PyObject *arg_list = PyList_New(0);
      $$ = PyObject_CallFunction(ParsedFunctionCallExpr, "OO", $1, arg_list);
      Py_DECREF(arg_list);
    </code>
    <code language="python">
      $$ = ParsedFunctionCallExpr($1, [])
    </code>
  </rule>
  <rule>
    <symbol>FUNCTION_NAME</symbol>
    <symbol>'('</symbol>
    <symbol>argumentList</symbol>
    <symbol>')'</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedFunctionCallExpr, "OO", $1, $3);
    </code>
    <code language="python">
      $$ = ParsedFunctionCallExpr($1, $3)
    </code>
  </rule>
</production>

<production name="16a">
  <non-terminal>argumentList</non-terminal>
  <rule>
    <symbol>argument</symbol>
    <code language="c">
      $$ = PyList_New(1);
      /* Steals a reference */
      PyList_SET_ITEM($$, 0, $1);
      Py_INCREF($1);
    </code>
    <code language="python">
      $$ = [$1]
    </code>
  </rule>
  <rule>
    <symbol>argumentList</symbol>
    <symbol>','</symbol>
    <symbol>argument</symbol>
    <code language="c">
      PyList_Append($1, $3);
      Py_INCREF($1);
      $$ = $1;
    </code>
    <code language="python">
      $1.append($3)
      $$ = $1
    </code>
  </rule>
</production>

<production name="17">
  <non-terminal>argument</non-terminal>
  <!-- Bypass -->
  <rule>
    <symbol>expr</symbol>
  </rule>
</production>

<production name="18">
  <non-terminal>unionExpr</non-terminal>
  <rule>
    <symbol>pathExpr</symbol>
  </rule>
  <rule>
    <symbol>unionExpr</symbol>
    <symbol>'|'</symbol>
    <symbol>pathExpr</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedUnionExpr, "OO", $1, $3);
    </code>
    <code language="python">
      $$ = ParsedUnionExpr($1, $3)
    </code>
  </rule>
</production>

<production name="19">
  <non-terminal>pathExpr</non-terminal>
  <rule>
    <symbol>locationPath</symbol>
  </rule>
  <rule>
    <symbol>filterExpr</symbol>
  </rule>
  <rule>
    <symbol>filterExpr</symbol>
    <symbol>'/'</symbol>
    <symbol>relativeLocationPath</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedPathExpr, "iOO", 0, $1, $3);
    </code>
    <code language="python">
      $$ = ParsedPathExpr($2, $1, $3)
    </code>
  </rule>
  <rule>
    <symbol>filterExpr</symbol>
    <symbol>DOUBLE_SLASH</symbol>
    <symbol>relativeLocationPath</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedPathExpr, "iOO", 1, $1, $3);
    </code>
    <code language="python">
      $$ = ParsedPathExpr($2, $1, $3)
    </code>
  </rule>
</production>

<production name="20">
  <non-terminal>filterExpr</non-terminal>
  <!-- Bypass -->
  <rule>
    <symbol>primaryExpr</symbol>
  </rule>
  <rule>
    <symbol>primaryExpr</symbol>
    <symbol>predicateList</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedFilterExpr, "OO", $1, $2);
    </code>
    <code language="python">
      $$ = ParsedFilterExpr($1, $2)
    </code>
  </rule>
</production>

<production name="21">
  <non-terminal>orExpr</non-terminal>
  <rule>
    <symbol>andExpr</symbol>
  </rule>
  <rule>
    <symbol>orExpr</symbol>
    <symbol>OR</symbol>
    <symbol>andExpr</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedOrExpr, "OO", $1, $3);
    </code>
    <code language="python">
      $$ = ParsedOrExpr($1, $3)
    </code>
  </rule>
</production>

<production name="22">
  <non-terminal>andExpr</non-terminal>
  <rule>
    <symbol>equalityExpr</symbol>
  </rule>
  <rule>
    <symbol>andExpr</symbol>
    <symbol>AND</symbol>
    <symbol>equalityExpr</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedAndExpr, "OO", $1, $3);
    </code>
    <code language="python">
      $$ = ParsedAndExpr($1, $3)
    </code>
  </rule>
</production>

<production name="23">
  <non-terminal>equalityExpr</non-terminal>
  <rule>
    <symbol>relationalExpr</symbol>
  </rule>
  <rule>
    <symbol>equalityExpr</symbol>
    <symbol>EQUALITY_OP</symbol>
    <symbol>relationalExpr</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedEqualityExpr, "OOO", $2, $1, $3);
    </code>
    <code language="python">
      $$ = ParsedEqualityExpr($2, $1, $3)
    </code>
  </rule>
</production>

<production name="24">
  <non-terminal>relationalExpr</non-terminal>
  <rule>
    <symbol>additiveExpr</symbol>
  </rule>
  <rule>
    <symbol>relationalExpr</symbol>
    <symbol>RELATIONAL_OP</symbol>
    <symbol>additiveExpr</symbol>
    <code language="c">
      char *op = PyString_AsString($2);
      if (op[0] == '&lt;') {
        if (op[1] == '=') {
          /* less than or equal to */
          $$ = PyObject_CallFunction(ParsedRelationalExpr, "lOO", 1, $1, $3);
        } else {
          /* less than */
          $$ = PyObject_CallFunction(ParsedRelationalExpr, "lOO", 0, $1, $3);
        }
      } else if (op[1] == '=') {
        /* greater than or equal to */
        $$ = PyObject_CallFunction(ParsedRelationalExpr, "lOO", 3, $1, $3);
      } else {
        /* greater than */
        $$ = PyObject_CallFunction(ParsedRelationalExpr, "lOO", 2, $1, $3);
      }    
    </code>
    <code language="python">
      ops = {'&lt;' : 0,
             '&gt;' : 2,
             '&lt;=' : 1,
             '&gt;=' : 3,
             }
      $$ = ParsedRelationalExpr(ops[$2], $1, $3)
    </code>
  </rule>
</production>

<production name="25">
  <non-terminal>additiveExpr</non-terminal>
  <rule>
    <symbol>multiplicativeExpr</symbol>
  </rule>
  <rule>
    <symbol>additiveExpr</symbol>
    <symbol>'+'</symbol>
    <symbol>multiplicativeExpr</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedAdditiveExpr, "iOO", 1, $1, $3);
    </code>
    <code language="python">
      $$ = ParsedAdditiveExpr(1, $1, $3)
    </code>
  </rule>
  <rule>
    <symbol>additiveExpr</symbol>
    <symbol>'-'</symbol>
    <symbol>multiplicativeExpr</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedAdditiveExpr, "iOO", -1, $1, $3);
    </code>
    <code language="python">
      $$ = ParsedAdditiveExpr(-1, $1, $3)
    </code>
  </rule>
</production>

<production name="26">
  <non-terminal>multiplicativeExpr</non-terminal>
  <rule>
    <symbol>unaryExpr</symbol>
  </rule>
  <rule>
    <symbol>multiplicativeExpr</symbol>
    <symbol>MULTIPLY_OPERATOR</symbol>
    <symbol>unaryExpr</symbol>
    <code language="c">
      char *op = PyString_AsString($2);
      switch (*op) {
        case '*': {
          $$ = PyObject_CallFunction(ParsedMultiplicativeExpr, "lOO", 0, $1, $3);
          break;
        }
        case 'd': {
          $$ = PyObject_CallFunction(ParsedMultiplicativeExpr, "lOO", 1, $1, $3);
          break;
        }
        case 'm': {
          $$ = PyObject_CallFunction(ParsedMultiplicativeExpr, "lOO", 2, $1, $3);
          break;
        }
      }
    </code>
    <code language="python">
      ops = {'*' : 0,
             'div' : 1,
             'mod' : 2,
             }
      $$ = ParsedMultiplicativeExpr(ops[$2], $1, $3)
    </code>
  </rule>
</production>

<production name="27">
  <non-terminal>unaryExpr</non-terminal>
  <rule>
    <symbol>unionExpr</symbol>
  </rule>
  <rule>
    <symbol>'-'</symbol>
    <symbol>unionExpr</symbol>
    <code language="c">
      $$ = PyObject_CallFunction(ParsedUnaryExpr, "O", $2);
    </code>
    <code language="python">
      $$ = ParsedUnaryExpr($2)
    </code>
  </rule>
</production>

</fragment>
