#include <execinfo.h>
#include <sstream>
#include <mutex>

inline void capture_stack_trace(std::stringstream &ss) {
    void* callstack[32];
    int frames = backtrace(callstack, 32);
    char** strs = backtrace_symbols(callstack, frames);
    for (int i = 0; i < frames; ++i) {
        ss << "\n  " << strs[i];
    }
    free(strs);
}

