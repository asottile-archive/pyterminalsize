/*
 * This is copied from python3.5 Modules/posixmodule.c
 * Modifications:
 * - Returns a normal tuple instead of a terminal size object
 */
#include <Python.h>

#if defined(MS_WINDOWS)
#include <windows.h>
#define TERMSIZE_USE_CONIO
#else
#include <sys/ioctl.h>
#include <termios.h>
#define TERMSIZE_USE_IOCTL
#endif

PyDoc_STRVAR(termsize__doc__,
    "Return the size of the terminal window as (columns, lines).\n"        \
    "\n"                                                                   \
    "The optional argument fd (default standard output) specifies\n"       \
    "which file descriptor should be queried.\n"                           \
    "\n"                                                                   \
    "If the file descriptor is not connected to a terminal, an OSError\n"  \
    "is thrown.\n"                                                         \
    "\n"                                                                   \
    "This function will only be defined if an implementation is\n"         \
    "available for this system.\n"                                         \
    "\n"                                                                   \
    "shutil.get_terminal_size is the high-level function which should \n"  \
    "normally be used, os.get_terminal_size is the low-level implementation.");

static PyObject*
get_terminal_size(PyObject *self, PyObject *args)
{
    int columns, lines;

    int fd = fileno(stdout);
    /* Under some conditions stdout may not be connected and
     * fileno(stdout) may point to an invalid file descriptor. For example
     * GUI apps don't have valid standard streams by default.
     *
     * If this happens, and the optional fd argument is not present,
     * the ioctl below will fail returning EBADF. This is what we want.
     */

    if (!PyArg_ParseTuple(args, "|i", &fd))
        return NULL;

#ifdef TERMSIZE_USE_IOCTL
    {
        struct winsize w;
        if (ioctl(fd, TIOCGWINSZ, &w))
            return PyErr_SetFromErrno(PyExc_OSError);
        columns = w.ws_col;
        lines = w.ws_row;
    }
#endif /* TERMSIZE_USE_IOCTL */
#ifdef TERMSIZE_USE_CONIO
    {
        DWORD nhandle;
        HANDLE handle;
        CONSOLE_SCREEN_BUFFER_INFO csbi;
        switch (fd) {
        case 0: nhandle = STD_INPUT_HANDLE;
            break;
        case 1: nhandle = STD_OUTPUT_HANDLE;
            break;
        case 2: nhandle = STD_ERROR_HANDLE;
            break;
        default:
            return PyErr_Format(PyExc_ValueError, "bad file descriptor");
        }
        handle = GetStdHandle(nhandle);
        if (handle == NULL)
            return PyErr_Format(PyExc_OSError, "handle cannot be retrieved");
        if (handle == INVALID_HANDLE_VALUE)
            return PyErr_SetFromWindowsErr(0);

        if (!GetConsoleScreenBufferInfo(handle, &csbi))
            return PyErr_SetFromWindowsErr(0);

        columns = csbi.srWindow.Right - csbi.srWindow.Left + 1;
        lines = csbi.srWindow.Bottom - csbi.srWindow.Top + 1;
    }
#endif /* TERMSIZE_USE_CONIO */

    return Py_BuildValue("nn", columns, lines);
}

static PyObject* set_terminal_size(PyObject* self, PyObject* args) {
    int fd;
    int columns;
    int lines;

    if (!PyArg_ParseTuple(args, "iii", &fd, &columns, &lines)) {
        return NULL;
    }

#ifdef TERMSIZE_USE_IOCTL
    {
        struct winsize w = {lines, columns, 0, 0};
        if (ioctl(fd, TIOCSWINSZ, &w))
            return PyErr_SetFromErrno(PyExc_OSError);
    }
#endif
#ifdef TERMSIZE_USE_CONIO
    {
        DWORD nhandle;
        HANDLE handle;
        SMALL_RECT w = {0, 0, columns - 1, lines - 1};
        switch (fd) {
        case 0: nhandle = STD_INPUT_HANDLE;
            break;
        case 1: nhandle = STD_OUTPUT_HANDLE;
            break;
        case 2: nhandle = STD_ERROR_HANDLE;
            break;
        default:
            return PyErr_Format(PyExc_ValueError, "bad file descriptor");
        }
        handle = GetStdHandle(nhandle);
        if (handle == NULL)
            return PyErr_Format(PyExc_OSError, "handle cannot be retrieved");
        if (handle == INVALID_HANDLE_VALUE)
            return PyErr_SetFromWindowsErr(0);
        if (!SetConsoleWindowInfo(handle, TRUE, &w))
            return PyErr_SetFromWindowsErr(0);
    }
#endif
    Py_INCREF(Py_None);
    return Py_None;
}


static struct PyMethodDef methods[] = {
    {"get_terminal_size", get_terminal_size, METH_VARARGS, termsize__doc__},
    {"set_terminal_size", set_terminal_size, METH_VARARGS, NULL},
    {NULL, NULL}
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT, "_pyterminalsize", NULL, -1, methods
};

PyMODINIT_FUNC PyInit__pyterminalsize(void) {
    return PyModule_Create(&module);
}
#else
PyMODINIT_FUNC init_pyterminalsize(void) {
    Py_InitModule3("_pyterminalsize", methods, NULL);
}
#endif
