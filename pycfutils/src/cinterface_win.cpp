#include <unordered_map>
#include <utility>
#include <vector>

#include <Windows.h>

#define LIBCINTERFACE_EXPORTS
#include "../include/pycfutils/cinterface.h"

#define SENTINEL 0x80000000


typedef std::unordered_map<DWORD, HHOOK> HookData;
typedef std::pair<int, int> XY;
typedef std::unordered_map<DWORD, std::vector<XY>> XYData;

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
            if (hookData.find(tid) != hookData.cend()) {
                auto xyIt = xyData[tid].cbegin();
                if (xyIt != xyData[tid].cend()) {
                    LPCBT_CREATEWNDW pcw = (LPCBT_CREATEWNDW)lParam;
                    if (pcw) {
                        LPCREATESTRUCTW pcs = pcw->lpcs;
                        if (pcs) {
                            if (xyIt->first != SENTINEL) {
                                pcs->x = xyIt->first;
                            }
                            if (xyIt->second != SENTINEL) {
                                pcs->y = xyIt->second;
                            }
                        }
                    }
                    xyData[tid].erase(xyIt);
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
    if (hookData.find(tid) == hookData.cend()) {
        HHOOK hook = SetWindowsHookExW(WH_CBT, _hookFunc, 0, tid);
        if (hook) {
            hookData[tid] = hook;
        }  // @TODO - cfati: Silently fail?
    }
    xyData[tid].emplace_back(std::make_pair(x, y));
    LeaveCriticalSection(&criticalSection);
    return MessageBoxW(hWnd, lpText, lpCaption, uType);
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

