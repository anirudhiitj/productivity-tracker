"""
Read Chrome session files to get ALL tabs (including background tabs)
"""
import os
import sqlite3
import json
from pathlib import Path

def find_chrome_profile_dir():
    """Find Chrome user data directory"""
    possible_paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default"),
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\Google\Chrome\User Data\Default"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def get_chrome_tabs_from_sessions():
    """Extract tabs from Chrome session files"""
    profile_dir = find_chrome_profile_dir()
    if not profile_dir:
        print("✗ Chrome profile directory not found")
        return []
    
    print(f"✓ Found Chrome profile: {profile_dir}\n")
    
    # Try reading Current Tabs file
    tabs_file = os.path.join(profile_dir, "Current Tabs")
    session_file = os.path.join(profile_dir, "Current Session")
    
    print(f"Checking files:")
    print(f"  - Current Tabs: {os.path.exists(tabs_file)}")
    print(f"  - Current Session: {os.path.exists(session_file)}")
    
    # These files are binary and Chrome-specific format
    # We'd need to parse SNSS (Chrome Session) format
    
    # Check if we can read History database instead (shows recent tabs)
    history_db = os.path.join(profile_dir, "History")
    if os.path.exists(history_db):
        try:
            # Copy to temp location (Chrome locks the file)
            import shutil
            import tempfile
            temp_db = os.path.join(tempfile.gettempdir(), "chrome_history_temp.db")
            shutil.copy2(history_db, temp_db)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Get recently visited URLs (might include currently open tabs)
            cursor.execute("""
                SELECT url, title, last_visit_time 
                FROM urls 
                ORDER BY last_visit_time DESC 
                LIMIT 50
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            print(f"\n✓ Found {len(rows)} recent URLs from History:\n")
            for i, (url, title, timestamp) in enumerate(rows[:20], 1):
                print(f"  {i}. {title or 'No title'}")
                print(f"     {url[:80]}\n")
            
            return rows
        except Exception as e:
            print(f"\n✗ Error reading History: {e}")
    
    return []

if __name__ == "__main__":
    print("\n=== Trying to Read Chrome Session Data ===\n")
    tabs = get_chrome_tabs_from_sessions()
    
    print("\n" + "="*70)
    print("NOTE: Chrome session files use proprietary binary format (SNSS)")
    print("To reliably get ALL open tabs, need one of:")
    print("  1. Chrome DevTools Protocol (restart Chrome with --remote-debugging-port=9222)")
    print("  2. Chrome Extension with tabs API access")
    print("  3. Parse binary SNSS format (complex)")
    print("="*70)
