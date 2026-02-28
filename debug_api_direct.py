"""Direct test of ProcessMonitor without HTTP"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.process_monitor import ProcessMonitor
from client.window_parser import WindowTitleParser

print("\n=== Testing ProcessMonitor directly ===\n")

# Test window enumeration first
print("1. Testing window enumeration:")
windows = WindowTitleParser.get_all_browser_windows()
print(f"   Total browser windows found: {len(windows)}")
chrome_windows = [(pid, title) for pid, title in windows if not WindowTitleParser.is_junk_window(title)]
print(f"   Non-junk windows: {len(chrome_windows)}")
for pid, title in chrome_windows[:5]:
    print(f"   - PID {pid}: {title[:80]}")

print("\n2. Testing ProcessMonitor.get_main_processes():")
print("   This may take a moment...")
try:
    pm = ProcessMonitor()
    processes = pm.get_main_processes()
    print(f"   ✓ Found {len(processes)} main processes")
    
    # Filter to Chrome/browser processes
    chrome_procs = [p for p in processes if 'chrome' in p['name'].lower() or 'firefox' in p['name'].lower() or 'edge' in p['name'].lower()]
    print(f"   ✓ Chrome/browser processes: {len(chrome_procs)}")
    print(f"   \n   DEBUG: Showing ALL browser process names:")
    for p in chrome_procs:
        name = p.get('name', 'UNKNOWN')
        title = p.get('window_title') or 'NO_TITLE'
        print(f"      - {name:30} | {title[:50]}")
    
    print("\n3. Chrome tabs with domains:")
    for i, proc in enumerate(chrome_procs[:15]):
        title = proc.get('window_title') or 'N/A'
        domain = proc.get('domain') or 'N/A'
        category = proc.get('category') or 'N/A'
        title_display = str(title)[:50] if title else 'N/A'
        mem = proc.get('memory_mb', 0)
        name = proc.get('name', 'unknown')
        pid = proc.get('pid', 0)
        print(f"   {i+1:2}. {domain:20} | {category:15} | {mem:6.1f}MB | PID {pid:6} | {name:20} | {title_display}")
    
    if len(chrome_procs) > 15:
        print(f"   ... and {len(chrome_procs) - 15} more")
        
except Exception as e:
    print(f"   ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===\n")
