"""Debug script to understand Chrome process and window mapping."""
import psutil
from client.window_parser import WindowTitleParser

print("\n=== ALL Chrome PROCESSES ===")
all_procs = []
for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
    try:
        if 'chrome' in proc.name().lower():
            mem_mb = proc.info['memory_info'].rss / (1024 * 1024)
            cpu = proc.info['cpu_percent'] or 0.0
            all_procs.append((proc.pid, proc.name(), mem_mb, cpu))
            print(f"PID: {proc.pid:6d} | {proc.name():20s} | RAM: {mem_mb:6.1f} MB | CPU: {cpu:5.1f}%")
    except:
        pass

print(f"\nTotal Chrome processes found: {len(all_procs)}")

print("\n=== WINDOWS FOR EACH Chrome PROCESS ===")
all_windows = WindowTitleParser.get_all_browser_windows()
print(f"Total browser windows enumerated: {len(all_windows)}\n")

# Group windows by process
windows_by_pid = {}
for pid, title in all_windows:
    if pid not in windows_by_pid:
        windows_by_pid[pid] = []
    windows_by_pid[pid].append(title)

for pid in sorted(windows_by_pid.keys()):
    print(f"PID {pid}: {len(windows_by_pid[pid])} windows")
    for title in windows_by_pid[pid][:2]:  # Show first 2
        clean_title = title[:60] if len(title) > 60 else title
        print(f"  - {clean_title}")
    if len(windows_by_pid[pid]) > 2:
        print(f"  ... and {len(windows_by_pid[pid])-2} more")

print("\n=== FILTER THRESHOLDS ===")
print(f"MIN_MEMORY_MB = 100")
print(f"MIN_CPU_PERCENT = 1.0")

passing = []
for pid, name, mem, cpu in all_procs:
    if mem >= 100 or cpu >= 1.0:
        passing.append((pid, name, mem, cpu))
        print(f"PASS: PID {pid} ({name}) - RAM: {mem:.1f}MB, CPU: {cpu:.1f}%")
    else:
        print(f"FAIL: PID {pid} ({name}) - RAM: {mem:.1f}MB, CPU: {cpu:.1f}%")

print(f"\nChrome processes passing filter: {len(passing)} out of {len(all_procs)}")
