#include <windows.h>
#include <stdio.h>

// Hook hdEAlignRotation in haydee.dll @ +0x127130
// __stdcall (no this, no params)

static void* orig_func = NULL;
static unsigned char orig_bytes[6];

void __stdcall hook_func() {
    FILE* f = fopen("C:\\Users\\Can\\AppData\\Local\\Temp\\opencode\\alignrot_log.txt", "a");
    if (f) { fprintf(f, "hdEAlignRotation called\n"); fclose(f); }
    
    HMODULE hHaydee = GetModuleHandleA("haydee.dll");
    DWORD funcAddr = (DWORD)hHaydee + 0x127130;
    DWORD oldProtect;
    VirtualProtect((void*)funcAddr, 6, PAGE_EXECUTE_READWRITE, &oldProtect);
    memcpy((void*)funcAddr, orig_bytes, 6);
    VirtualProtect((void*)funcAddr, 6, oldProtect, &oldProtect);
    
    ((void(__stdcall*)())orig_func)();
    
    VirtualProtect((void*)funcAddr, 6, PAGE_EXECUTE_READWRITE, &oldProtect);
    DWORD offset = (DWORD)hook_func - funcAddr - 5;
    unsigned char jump[5] = { 0xE9, 0, 0, 0, 0 };
    memcpy(jump + 1, &offset, 4);
    memcpy((void*)funcAddr, jump, 5);
    VirtualProtect((void*)funcAddr, 6, oldProtect, &oldProtect);
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    if (ul_reason_for_call == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(hModule);
        HMODULE hHaydee = GetModuleHandleA("haydee.dll");
        if (!hHaydee) return TRUE;
        DWORD funcAddr = (DWORD)hHaydee + 0x127130;
        orig_func = (void*)funcAddr;
        DWORD oldProtect;
        VirtualProtect((void*)funcAddr, 6, PAGE_EXECUTE_READWRITE, &oldProtect);
        memcpy(orig_bytes, (void*)funcAddr, 6);
        DWORD offset = (DWORD)hook_func - funcAddr - 5;
        unsigned char jump[5] = { 0xE9, 0, 0, 0, 0 };
        memcpy(jump + 1, &offset, 4);
        memcpy((void*)funcAddr, jump, 5);
        VirtualProtect((void*)funcAddr, 6, oldProtect, &oldProtect);
        
        FILE* f = fopen("C:\\Users\\Can\\AppData\\Local\\Temp\\opencode\\payload_loaded.txt", "w");
        if (f) { fprintf(f, "Hooked hdEAlignRotation\n"); fclose(f); }
    }
    return TRUE;
}
