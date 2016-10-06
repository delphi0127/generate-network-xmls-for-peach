#ifndef DOMLETTE_PROCESSING_INSTRUCTION_H
#define DOMLETTE_PROCESSING_INSTRUCTION_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"
#include "node.h"

  typedef struct {
    PyNode_HEAD
    PyObject *nodeName;
    PyObject *nodeValue;
  } PyProcessingInstructionObject;

#define ProcessingInstruction_GET_TARGET(op) \
(((PyProcessingInstructionObject *)(op))->nodeName)
#define ProcessingInstruction_GET_DATA(op) \
(((PyProcessingInstructionObject *)(op))->nodeValue)

  extern PyTypeObject DomletteProcessingInstruction_Type;

#define PyProcessingInstruction_Check(op) \
PyObject_TypeCheck(op, &DomletteProcessingInstruction_Type)
#define PyProcessingInstruction_CheckExact(op) \
((op)->ob_type == &DomletteProcessingInstruction_Type)

  /* Module Methods */
  int DomletteProcessingInstruction_Init(PyObject *module);
  void DomletteProcessingInstruction_Fini(void);

  /* ProcessingInstruction Methods */
  PyProcessingInstructionObject *ProcessingInstruction_New(
    PyDocumentObject *ownerDocument, PyObject *target, PyObject *data);

  PyProcessingInstructionObject *ProcessingInstruction_CloneNode(
    PyObject *node, int deep, PyDocumentObject *newOwnerDocument);

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_PROCESSING_INSTRUCTION_H */
