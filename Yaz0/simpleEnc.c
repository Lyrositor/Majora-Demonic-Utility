/*
 * Yaz0 Simple Encoding Scheme
 * Source: http://vg64tools.googlecode.com/svn/pc/z64porter/trunk/yaz0.c
 */

#include <Python.h>

// Simple and straight encoding scheme for Yaz0.
uint32_t simpleEnc(uint8_t* src, int size, int pos, uint32_t *pMatchPos) {

    int startPos = pos - 0x1000, j, i;
    uint32_t numBytes = 1;
    uint32_t matchPos = 0;

    if (startPos < 0)
        startPos = 0;
    for (i = startPos; i < pos; i++) {
        for (j = 0; j < size-pos; j++) {
            if (src[i + j] != src[j + pos])
                break;
        }
        if (j > numBytes) {
            numBytes = j;
            matchPos = i;
        }
    }
    *pMatchPos = matchPos;
    if (numBytes == 2)
        numBytes = 1;
    return numBytes;
}

// The Python simpleEnc function.
static PyObject *simpleEnc_encode(PyObject *self, PyObject *args) {

    PyBytesObject *srcObj;
    uint8_t *src;
    int srcSize;
    int pos;
    uint32_t numBytes;
    uint32_t matchPos;

    if (!PyArg_ParseTuple(args, "Oi", &srcObj, &pos))
        return NULL;

    src = (uint8_t *) PyBytes_AsString((PyObject*) srcObj);
    srcSize = PySequence_Length((PyObject*) srcObj);
    numBytes = simpleEnc(src, srcSize, pos, &matchPos);
    return Py_BuildValue("ii", numBytes, matchPos);
}

static PyMethodDef simpleEncMethods[] = {
     {"encode", simpleEnc_encode, METH_VARARGS, ""},
     {NULL, NULL, 0, NULL}
};

static struct PyModuleDef simpleEncmodule = {
   PyModuleDef_HEAD_INIT,
   "simpleEnc",
   NULL,
   -1,
   simpleEncMethods
};

// The Python module initialization functions.
PyMODINIT_FUNC PyInit_simpleEnc(void) {
    return PyModule_Create(&simpleEncmodule);
}
