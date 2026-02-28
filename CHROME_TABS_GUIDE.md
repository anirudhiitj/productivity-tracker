# How to See ALL Chrome Tabs (Including Background Tabs)

## Current Limitation
The system currently shows **9 Chrome tabs** (only active tabs in each Chrome window).
You mentioned GitHub, Claude, HackSprint aren't showing - these are likely **background tabs**.

## Solution: Enable Chrome DevTools Protocol

### Step 1: Launch Chrome with DevTools
Run this script to restart Chrome with full tab access:
```
launch_chrome_devtools.bat
```

**What it does:**
- Closes all Chrome instances
- Restarts Chrome with DevTools Protocol enabled (port 9222)
- Allows tracking of ALL tabs (active + background)

### Step 2: Reopen Your Tabs
After Chrome restarts:
1. Chrome will restore your previous session
2. Or manually reopen GitHub, Claude, HackSprint, etc.

### Step 3: Verify  
The productivity tracker will now show **ALL Chrome tabs**, including:
- ✅ Active tabs in each window
- ✅ Background tabs (GitHub, Claude, HackSprint, etc.)
- ✅ Tabs in minimized windows
- ✅ Tabs across all Chrome profiles

---

## Current vs. Enhanced Mode

### Without DevTools (Current)
- Shows: **9 tabs** (only active tab per Chrome window)
- Missing: Background tabs like GitHub, Claude, HackSprint

### With DevTools (Enhanced)
- Shows: **ALL tabs** (20+ tabs including all background ones)
- Includes: Every single open tab, even if not visible

---

## Alternative (If you don't want to restart Chrome)

The system will continue working with window enumeration:
- Switch to a tab to make it "active" → it will appear in the tracker
- The 9 tabs currently showing are the active tabs in your 9 Chrome windows

---

## How Clicking Works

Each Chrome tab will be a **separate clickable entry**:
```
1. GitHub - anirudhiitj/productivity-tracker    [Click to focus]
2. Claude AI Chat                                [Click to focus]
3. HackSprint                                    [Click to focus]
4. YouTube - FastAPI Tutorial                    [Click to focus]
5. Google Gemini                                 [Click to focus]
... (all your tabs individually)
```

When you click one, only that specific tab comes to foreground.

---

**Ready?** Run `launch_chrome_devtools.bat` to see ALL your tabs!
