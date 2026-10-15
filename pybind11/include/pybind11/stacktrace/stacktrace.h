#include <pybind11/pybind11.h>
#include <stdexcept>
#include <sstream>

#ifdef _WIN32
    #include <pybind11/stacktrace/win.h>
#else
    #include <pybind11/stacktrace/nix.h>
#endif

inline auto verbose_translator = [](std::exception_ptr p) {
    std::stringstream ss;
    ss << "\n--- C++ Native Stack Trace ---";
    try {
        if (p) std::rethrow_exception(p);
    } catch (const std::exception& e) {
        ss << e.what() << "\n";
    } catch (...) {
        ss << "Unknown Exception Type\n";
    }
    capture_stack_trace(ss);
    PyErr_SetString(PyExc_Exception, ss.str().c_str());
};

