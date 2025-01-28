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