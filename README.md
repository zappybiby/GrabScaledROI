# GrabScaledROI

Python tool that captures the active window, lets you select a **Region of Interest (ROI)** within that window, and then prints a neatly organized summary of the ROI coordinates (window-relative, absolute, and normalized).

## Why Use This Tool

When working on computer vision projects or automation tasks, you often need coordinates from a specific part of the screen or an application window. However, if you **share** your code with others or deploy it on different screens, the hard-coded coordinates may no longer match. 

By using this tool, you can **normalize** ROIs, making it possible to re-scale them to fit any window or screen size. This saves time, reduces confusion, and helps ensure consistent results across diverse environments.

---

## Features

1. **Captures the active window** and prompts you to **select an ROI** using an OpenCV UI.  
2. **Outputs** three categories of ROI info:
   - **Window-Relative**: `(x, y, w, h)` within the window.  
   - **Absolute**: Screen-based edges and corner coordinates.  
   - **Normalized**: `(x, y, w, h)` as fractions of the active window size (for easy scaling).  
3. Supports **single-run mode** (exits immediately after one ROI capture) or **continuous mode** (capturing multiple ROIs until you press `Esc`).  
4. **Configurable capture key** (default: `o`).

Example Output:
```
===== ROI SUMMARY =====
Monitor Resolution:             1920 x 1080
Active Window Title:            zappybiby/GrabScaledROI: Grab ROI and Normalize Coords - Google Chrome
Active Window Size:             1936 x 1056

ROI (Window-Relative):
  Rectangle: x=368, y=468, w=354, h=394
  Corners:
    top-left     = (368, 468)
    top-right    = (722, 468)
    bottom-left  = (368, 862)
    bottom-right = (722, 862)

ROI (Absolute):
  Rectangle: left=360, top=460, right=714, bottom=854
  Corners:
    top-left     = (360, 460)
    top-right    = (714, 460)
    bottom-left  = (360, 854)
    bottom-right = (714, 854)

ROI (Normalized to Window):
  Rectangle: x=0.1901, y=0.4432, w=0.1829, h=0.3731
  Corners:
    top-left     = (0.1901, 0.4432)
    top-right    = (0.3729, 0.4432)
    bottom-left  = (0.1901, 0.8163)
    bottom-right = (0.3729, 0.8163)
===== END OF ROI INFO =====
```
