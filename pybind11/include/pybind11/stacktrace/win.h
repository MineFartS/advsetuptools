#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <dbghelp.h>
#pragma comment(lib, "dbghelp.lib")

#include <stdexcept>
#include <sstream>

thread_local std::string t_last_crash_trace = "";

LONG WINAPI NativeCrashVectoredHandler(PEXCEPTION_POINTERS exception_info) {

    EXCEPTION_RECORD* record = exception_info->ExceptionRecord;
    if (
        record->ExceptionCode != 0xE06D7363 ||
        record->NumberParameters < 3 ||
        record->ExceptionInformation[0] != 0x19930520 ||
        !t_last_crash_trace.empty()
    ) return EXCEPTION_CONTINUE_SEARCH;
        
    std::stringstream ss;

    HANDLE process = GetCurrentProcess();
    HANDLE thread = GetCurrentThread();
    CONTEXT context = *exception_info->ContextRecord; 

    SymInitialize(process, NULL, TRUE);

    STACKFRAME64 frame = {};
    frame.AddrPC.Offset    = context.Rip;
    frame.AddrPC.Mode      = AddrModeFlat;
    frame.AddrFrame.Offset = context.Rbp;
    frame.AddrFrame.Mode   = AddrModeFlat;
    frame.AddrStack.Offset = context.Rsp;
    frame.AddrStack.Mode   = AddrModeFlat;

    IMAGEHLP_LINE64 line = {};
    line.SizeOfStruct = sizeof(IMAGEHLP_LINE64);

    DWORD disp = 0;
    while (StackWalk64(
        IMAGE_FILE_MACHINE_AMD64, 
        process, thread, 
        &frame, &context, NULL, 
        SymFunctionTableAccess64, 
        SymGetModuleBase64, NULL
    )) {
        if (frame.AddrPC.Offset == 0)
            break;
        if (SymGetLineFromAddr64(process, frame.AddrPC.Offset, &disp, &line))
            ss << "\n  " << line.FileName << " : " << std::dec << line.LineNumber;
    }

    SymCleanup(process);
    t_last_crash_trace = ss.str();

    return EXCEPTION_CONTINUE_SEARCH; 
}

inline void capture_stack_trace(std::stringstream &ss) {
    ss << t_last_crash_trace;
    t_last_crash_trace.clear();
};


