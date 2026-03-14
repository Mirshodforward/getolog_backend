#!/usr/bin/env python3
"""
Kill all bot-related Python processes
"""
import psutil
import os
import sys


def kill_all_processes():
    """Kill all bot processes"""
    current_pid = os.getpid()
    killed_count = 0
    
    print("🔍 Barcha jarayonlar qidirilmoqda...")
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Eski bot jarayonlarini o'chirish
            cmdline_list = proc.cmdline()
            if cmdline_list is None:
                cmdline_list = []
            cmdline = ' '.join(cmdline_list)
            proc_name = proc.name() if callable(proc.name) else proc.name
            
            if proc.pid != current_pid and ('client_bot' in cmdline or 'python' in proc_name):
                if 'main.py' in cmdline or 'client_bot' in cmdline:
                    print(f"❌ Jarayon o'chirilmoqda: PID={proc.pid}, Command={cmdline[:60]}")
                    proc.kill()
                    killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    print(f"\n✅ {killed_count} ta jarayon o'chirildi!")


if __name__ == "__main__":
    try:
        kill_all_processes()
    except Exception as e:
        print(f"❌ Xato: {e}")
        sys.exit(1)
