#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <tlhelp32.h>

int main(int argc, char* argv[]) {
    if (argc < 3) {
        printf("Usage: injector.exe <process_name> <dll_path>\n");
        return 1;
    }
    
    const char* procName = argv[1];
    const char* dllPath = argv[2];
    
    HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (snapshot == INVALID_HANDLE_VALUE) {
        printf("Failed to create snapshot\n");
        return 1;
    }
    
    PROCESSENTRY32 pe;
    pe.dwSize = sizeof(pe);
    DWORD pid = 0;
    if (Process32First(snapshot, &pe)) {
        do {
            if (_stricmp(pe.szExeFile, procName) == 0) {
                pid = pe.th32ProcessID;
                break;
            }
        } while (Process32Next(snapshot, &pe));
    }
    CloseHandle(snapshot);
    
    if (pid == 0) {
        printf("Process '%s' not found\n", procName);
        return 1;
    }
    
    printf("Found %s (PID %lu)\n", procName, pid);
    
    HANDLE hProc = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
    if (!hProc) {
        printf("Failed to open process (error %lu)\n", GetLastError());
        return 1;
    }
    
    size_t pathLen = strlen(dllPath) + 1;
    void* remoteMem = VirtualAllocEx(hProc, NULL, pathLen, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (!remoteMem) {
        printf("Failed to allocate memory\n");
        CloseHandle(hProc);
        return 1;
    }
    
    if (!WriteProcessMemory(hProc, remoteMem, dllPath, pathLen, NULL)) {
        printf("Failed to write memory\n");
        VirtualFreeEx(hProc, remoteMem, 0, MEM_RELEASE);
        CloseHandle(hProc);
        return 1;
    }
    
    HMODULE hKernel32 = GetModuleHandleA("kernel32.dll");
    FARPROC loadLib = GetProcAddress(hKernel32, "LoadLibraryA");
    
    HANDLE hThread = CreateRemoteThread(hProc, NULL, 0, (LPTHREAD_START_ROUTINE)loadLib, remoteMem, 0, NULL);
    if (!hThread) {
        printf("Failed to create thread (error %lu)\n", GetLastError());
        VirtualFreeEx(hProc, remoteMem, 0, MEM_RELEASE);
        CloseHandle(hProc);
        return 1;
    }
    
    WaitForSingleObject(hThread, INFINITE);
    
    DWORD exitCode;
    GetExitCodeThread(hThread, &exitCode);
    printf("LoadLibrary returned: 0x%lx\n", exitCode);
    
    CloseHandle(hThread);
    VirtualFreeEx(hProc, remoteMem, 0, MEM_RELEASE);
    CloseHandle(hProc);
    
    return (exitCode == 0) ? 1 : 0;
}
