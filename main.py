import time
import keyboard
import pygetwindow as gw
import pyautogui
import cv2
import numpy as np

# Toggle continuous (multiple ROIs) or single-run (exits after one capture).
CONTINUOUS_MODE = False
CAPTURE_KEY = 'o'  # Press this to capture the ROI


def capture_active_window_and_select_roi():
    """Capture the active window, let the user select an ROI, and print structured ROI info."""
    active_window = gw.getActiveWindow()
    if not active_window:
        print("No active window detected.")
        return

    screen_w, screen_h = pyautogui.size()
    win_left = active_window.left
    win_top = active_window.top
    win_w = active_window.width
    win_h = active_window.height
    win_title = active_window.title

    screenshot = pyautogui.screenshot(region=(win_left, win_top, win_w, win_h))
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    x_rel, y_rel, w_rel, h_rel = cv2.selectROI("Select ROI", screenshot_cv, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow("Select ROI")

    if w_rel == 0 or h_rel == 0:
        print("ROI selection canceled or invalid.")
        return

    # Absolute rectangle
    abs_left = win_left + x_rel
    abs_top = win_top + y_rel
    abs_right = abs_left + w_rel
    abs_bottom = abs_top + h_rel

    # Window-relative corners
    rel_top_left = (x_rel, y_rel)
    rel_top_right = (x_rel + w_rel, y_rel)
    rel_bottom_left = (x_rel, y_rel + h_rel)
    rel_bottom_right = (x_rel + w_rel, y_rel + h_rel)

    # Absolute corners
    abs_top_left = (abs_left, abs_top)
    abs_top_right = (abs_right, abs_top)
    abs_bottom_left = (abs_left, abs_bottom)
    abs_bottom_right = (abs_right, abs_bottom)

    # Normalized rectangle (relative to the window)
    x_norm = x_rel / win_w
    y_norm = y_rel / win_h
    w_norm = w_rel / win_w
    h_norm = h_rel / win_h

    # Normalized corners
    norm_top_left = (x_norm, y_norm)
    norm_top_right = (x_norm + w_norm, y_norm)
    norm_bottom_left = (x_norm, y_norm + h_norm)
    norm_bottom_right = (x_norm + w_norm, y_norm + h_norm)

    print("\n===== ROI SUMMARY =====")
    print(f"Monitor Resolution:             {screen_w} x {screen_h}")
    print(f"Active Window Title:            {win_title}")
    print(f"Active Window Size:             {win_w} x {win_h}")

    print("\nROI (Window-Relative):")
    print(f"  Rectangle: x={x_rel}, y={y_rel}, w={w_rel}, h={h_rel}")
    print("  Corners:")
    print(f"    top-left     = {rel_top_left}")
    print(f"    top-right    = {rel_top_right}")
    print(f"    bottom-left  = {rel_bottom_left}")
    print(f"    bottom-right = {rel_bottom_right}")

    print("\nROI (Absolute):")
    print(f"  Rectangle: left={abs_left}, top={abs_top}, right={abs_right}, bottom={abs_bottom}")
    print("  Corners:")
    print(f"    top-left     = {abs_top_left}")
    print(f"    top-right    = {abs_top_right}")
    print(f"    bottom-left  = {abs_bottom_left}")
    print(f"    bottom-right = {abs_bottom_right}")

    print("\nROI (Normalized to Window):")
    print(f"  Rectangle: x={x_norm:.4f}, y={y_norm:.4f}, w={w_norm:.4f}, h={h_norm:.4f}")
    print("  Corners:")
    print(f"    top-left     = ({norm_top_left[0]:.4f}, {norm_top_left[1]:.4f})")
    print(f"    top-right    = ({norm_top_right[0]:.4f}, {norm_top_right[1]:.4f})")
    print(f"    bottom-left  = ({norm_bottom_left[0]:.4f}, {norm_bottom_left[1]:.4f})")
    print(f"    bottom-right = ({norm_bottom_right[0]:.4f}, {norm_bottom_right[1]:.4f})")

    print("===== END OF ROI INFO =====\n")


def main():
    print(f"Press '{CAPTURE_KEY}' to capture the active window and select ROI.")
    if CONTINUOUS_MODE:
        print("Press 'esc' to exit (continuous mode).")
    else:
        print("Script will exit after one ROI capture (single-run mode).")

    if CONTINUOUS_MODE:
        while True:
            if keyboard.is_pressed(CAPTURE_KEY):
                capture_active_window_and_select_roi()
                time.sleep(1)
            if keyboard.is_pressed('esc'):
                print("Exiting (continuous mode).")
                break
            time.sleep(0.1)
    else:
        while True:
            if keyboard.is_pressed(CAPTURE_KEY):
                capture_active_window_and_select_roi()
                break
            time.sleep(0.1)


if __name__ == "__main__":
    main()
