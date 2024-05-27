#include <unordered_map>
#include <utility>

#include <Windows.h>

#define LIBCINTERFACE_EXPORTS
#include "../include/pycfutils/cinterface.h"

#define SENTINEL 0x80000000


typedef std::unordered_map<DWORD, HHOOK> HookData;
typedef std::pair<int, int> XY;
typedef std::unordered_map<DWORD, XY> XYData;

CRITICAL_SECTION criticalSection;
XYData xyData;
HookData hookData;


static LRESULT CALLBACK _hookFunc(int nCode, WPARAM wParam, LPARAM lParam)
{
    if (nCode < 0) {
        return CallNextHookEx(NULL, nCode, wParam, lParam);
    }
    switch (nCode) {
        case HCBT_CREATEWND: {
            EnterCriticalSection(&criticalSection);
            DWORD tid = GetCurrentThreadId();
            HookData::const_iterator hIt = hookData.find(tid);
            if (hIt != hookData.cend()) {
                XYData::const_iterator xyIt = xyData.find(tid);
                if (xyIt != xyData.cend()) {
                    LPCBT_CREATEWNDW pcw = (LPCBT_CREATEWNDW)lParam;
                    if (pcw) {
                        LPCREATESTRUCTW pcs = pcw->lpcs;
                        if (pcs) {
                            if (xyIt->second.first != SENTINEL) {
                                pcs->x = xyIt->second.first;
                            }
                            if (xyIt->second.second != SENTINEL) {
                                pcs->y = xyIt->second.second;
                            }
                        }
                    }
                    xyData.erase(xyIt);
                }
                if (UnhookWindowsHookEx(hIt->second)) {  // @TODO - cfati: Unhook from within hook
                    hookData.erase(hIt);
                }
            }
            LeaveCriticalSection(&criticalSection);
            break;
        }
        default: {
            break;
        }
    }
    return CallNextHookEx(NULL, nCode, wParam, lParam);
}

int MessageBoxXY(HWND hWnd, LPCWSTR lpText, LPCWSTR lpCaption, UINT uType, int x, int y)
{
    EnterCriticalSection(&criticalSection);
    DWORD tid = GetCurrentThreadId();
    int err = 0;
    if (hookData.find(tid) == hookData.cend()) {
        HHOOK hook = SetWindowsHookExW(WH_CBT, _hookFunc, 0, tid);
        if (hook) {
            hookData.emplace(std::make_pair(tid, hook));
        }
        else {
            err = GetLastError();
        }
    } else {
        err = -1;
    }
    if (!err) {
        xyData.emplace(std::make_pair(tid, std::make_pair(x, y)));
    }
    LeaveCriticalSection(&criticalSection);
    return err ? err : MessageBoxW(hWnd, lpText, lpCaption, uType);
}


int clearHooks()
{
    int ret = 0;
    EnterCriticalSection(&criticalSection);
    for (auto it = hookData.cbegin(); it != hookData.cend(); ++it) {
        if (UnhookWindowsHookEx(it->second)) {
            ++ret;
        }  // @TODO - cfati: Silently fail?
    }
    LeaveCriticalSection(&criticalSection);
    return ret;
}


BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved)
{
    // Perform actions based on the reason for calling.
    switch (fdwReason) {
        case DLL_PROCESS_ATTACH: {
            // Initialize once for each new process.
            // Return FALSE to fail DLL load.
            InitializeCriticalSection(&criticalSection);
            break;
        }
        case DLL_THREAD_ATTACH: {
            // Do thread-specific initialization.
            break;
        }
        case DLL_THREAD_DETACH: {
            // Do thread-specific cleanup.
            break;
        }
        case DLL_PROCESS_DETACH: {

            if (lpvReserved != NULL) {
                break; // do not do cleanup if process termination scenario
            }
            DeleteCriticalSection(&criticalSection);
            // Perform any necessary cleanup.
            break;
        }
        default: {
            break;
        }
    }
    return TRUE;  // Successful DLL_PROCESS_ATTACH.
}

