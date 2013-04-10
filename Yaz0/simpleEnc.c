/*
 *  Majora's Demonic Utility - all-in-one editor for Majora's Mask.
 *  Copyright (C) 2013  Lyrositor <gagne.marc@gmail.com>
 *
 *  This file is part of Majora's Demonic Utility.
 *
 *  Majora's Demonic Utility is free software: you can redistribute it and/or
 *  modify it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  Majora's Demonic Utility is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with Majora's Demonic Utility.  If not, see
 *  <http://www.gnu.org/licenses/>.
 */

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
