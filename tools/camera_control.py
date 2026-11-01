#!/usr/bin/env python3
"""
EML Camera Control Daemon

Translates right-click + WASD into scroll wheel events for Edith.
For users with broken scroll wheels.

Usage: python camera_control.py
Press Ctrl+C to stop.
"""

import ctypes
import time
import sys

# Windows API
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Virtual key codes
VK_W = 0x57
VK_A = 0x41
VK_S = 0x53
VK_D = 0x44
VK_RBUTTON = 0x02

# Mouse wheel event
MOUSEEVENTF_WHEEL = 0x0800
WHEEL_DELTA = 120

# Check if a key is pressed
def is_key_pressed(vk):
    return (user32.GetAsyncKeyState(vk) & 0x8000) != 0

# Check if right mouse button is held
def is_rmb_held():
    return (user32.GetAsyncKeyState(VK_RBUTTON) & 0x8000) != 0

# Send scroll wheel event
def scroll(delta):
    user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, delta, 0)

# Get foreground window title
def get_foreground_title():
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value

print("EML Camera Control Daemon")
print("Translates right-click + WASD into scroll wheel for Edith.")
print("Hold right-click and press WASD to move camera.")
print("Press Ctrl+C to stop.\n")

# Track last state to avoid spamming
was_rmb = False
was_w = False
was_s = False

try:
    while True:
        title = get_foreground_title()
        edith_active = "Edith" in title or "edith" in title.lower()
        
        if edith_active:
            rmb = is_rmb_held()
            w = is_key_pressed(VK_W)
            s = is_key_pressed(VK_S)
            
            if rmb:
                if w and not was_w:
                    scroll(WHEEL_DELTA)  # scroll up
                    was_w = True
                elif not w:
                    was_w = False
                
                if s and not was_s:
                    scroll(-WHEEL_DELTA)  # scroll down
                    was_s = True
                elif not s:
                    was_s = False
            else:
                was_w = False
                was_s = False
        
        time.sleep(0.05)  # 20 Hz polling
except KeyboardInterrupt:
    print("\nStopped.")
