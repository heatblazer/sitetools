#include <Python.h>
#include <stdio.h>
#include <stdint.h>

static char module_docstring[] =
        "This module provides swap in 4 and swap in 2 functions";

static char endianSwap32_docstring[] =
        "Flip bytes in a 32 bit integers";

static char endianSwap16_docstring[] =
        "Flip bytes in a 16 bit integers";

static const char genutf8_docstring[] =
    "Generate UTF8 sequences";


static PyObject* genutf81(PyObject* self, PyObject* args)
{
    char *a = NULL;
    if (!PyArg_ParseTuple(args, "z", &a)) {
        return NULL;
    } else {
        return Py_BuildValue("z", a);
    }
}

static PyObject* genutf82(PyObject* self, PyObject* args)
{
    const char *a = NULL;
    if (!PyArg_ParseTuple(args, "z", &a)) {
        return NULL;
    } else {
        char b[3] = {
            (char)(3<<6),
            (char)(1 << 7),
            a[0]
        };
        return Py_BuildValue("y", b);
    }
}

static PyObject* genutf83(PyObject* self, PyObject* args)
{
    const char *a = NULL;
    if (!PyArg_ParseTuple(args, "z", &a)) {
        return NULL;
    } else {
        char b[4] = {
            (char)(7<<5),
            (char)(1 << 7),
            (char)(1<<7),
            a[0]
        };
        return Py_BuildValue("y", b);
    }
}

static PyObject* genutf84(PyObject* self, PyObject* args)
{
    const char *a = NULL;
    if (!PyArg_ParseTuple(args, "z", &a)) {
        return NULL;
    } else {
        char b[5] = {
            (char)(0xF << 4),
            (char)(1 << 7),
            (char)(1 << 7),
            (char)(1 << 7),
            a[0]
        };
        return Py_BuildValue("y", b);
    }
}

static PyObject* endianSwap16(PyObject* self, PyObject* args)
{
    short a;
    if (!PyArg_ParseTuple(args, "i", &a)) {
        return NULL;
    } else {
        short b = (int16_t) ((a << 8) | (a >> 8));
        return Py_BuildValue("i", b);
    }
}

static PyObject* endianSwap32(PyObject* self, PyObject* args)
{
    int a;
    if (!PyArg_ParseTuple(args, "i", &a)) {
        return NULL;
    } else {
        int b = (int32_t) (((a << 24) & 0xff000000) |
                                       ((a << 8) & 0x00ff0000) |
                                       ((a >> 8) & 0x0000ff00) |
                                       ((a >> 24) & 0x000000ff));
        return Py_BuildValue("i", b);
    }
}

/* describe a module containing the interfaces,
 * function pointer and a  doc string, some explaination
 * about the function (document)
 * */
static PyMethodDef module_methods[] = {
    {"endianSwap16", endianSwap16, METH_VARARGS, endianSwap16_docstring},
    {"endianSwap32", endianSwap32, METH_VARARGS, endianSwap32_docstring},
    {"genutf81", genutf81, METH_VARARGS, genutf8_docstring},
    {"genutf82", genutf82, METH_VARARGS, genutf8_docstring},
    {"genutf83", genutf83, METH_VARARGS, genutf8_docstring},
    {"genutf84", genutf84, METH_VARARGS, genutf8_docstring}
    };


static struct PyModuleDef simplemodule = {
    PyModuleDef_HEAD_INIT,
    "simplemodule",
    "Byte maniplator stuff and utf8 generators",
    -1,
    module_methods
};

#if 0
PyMODINIT_FUNC initlibsimplemodule(void)
{
    (void) Py_InitModule("libsimplemodule", module_methods);
}
#else
PyMODINIT_FUNC PyInit_simplemodule(void) {
    return PyModule_Create(&simplemodule);
}
#endif

#if 0
int main(int argc, char** argv)
{
    Py_SetProgramName(argv[0]);
    Py_Initialize();
    initlibsimplemodule();
    return 0;
}
#endif
