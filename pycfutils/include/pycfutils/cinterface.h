// LibCInterface prototypes
#pragma once

#if defined(_WIN32)
#  if defined(LIBCINTERFACE_STATIC)
#    define LIBCINTERFACE_EXPORT_API
#  else  // LIBCINTERFACE_STATIC
#    if defined(LIBCINTERFACE_EXPORTS)
#      define LIBCINTERFACE_EXPORT_API __declspec(dllexport)
#    else  // LIBCINTERFACE_EXPORTS
#      define LIBCINTERFACE_EXPORT_API __declspec(dllimport)
#    endif  // LIBCINTERFACE_EXPORTS
#  endif  // LIBCINTERFACE_STATIC
#else  // _WIN32
#  define LIBCINTERFACE_EXPORT_API
#endif  // _WIN32

#if defined(_WIN32)
#  include <Windows.h>
#else  // _WIN32
#endif  // _WIN32

#if defined(__cplusplus)
extern "C" {
#endif  // __cplusplus

#  if defined(_WIN32)

LIBCINTERFACE_EXPORT_API int MessageBoxXY(HWND hWnd, LPCWSTR lpText, LPCWSTR lpCaption, UINT uType, int x, int y);
LIBCINTERFACE_EXPORT_API int clearHooks();

#  else  // _WIN32
#  endif  // _WIN32

#if defined(__cplusplus)
}
#endif  // __cplusplus

