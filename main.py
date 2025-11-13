import time
import os
import argparse
from datetime import datetime

import keyboard
import pygetwindow as gw
import pyautogui
import cv2
import numpy as np

CAPTURE_KEY = 'o'  # Press this to capture the ROI
SAVED_ROI_ROOT = "Saved ROIs"


def get_top_k_colors_kmeans(roi_bgr, k=3):
    """
    Given an ROI in BGR (uint8), run KMeans to get top-k dominant colors.
    Returns a list of dicts with BGR, Hex, HSV (OpenCV range), and percentage.
    """
    pixels = roi_bgr.reshape((-1, 3))
    pixels = np.float32(pixels)

    num_pixels = pixels.shape[0]
    if num_pixels == 0:
        return []

    k = min(k, num_pixels)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    compactness, labels, centers = cv2.kmeans(
        pixels,
        k,
        None,
        criteria,
        10,
        cv2.KMEANS_RANDOM_CENTERS
    )

    labels = labels.flatten()
    centers = np.uint8(centers)

    unique_labels, counts = np.unique(labels, return_counts=True)
    sort_idx = np.argsort(-counts)

    sorted_centers = centers[sort_idx]
    sorted_counts = counts[sort_idx]

    colors = []
    total_pixels = float(num_pixels)

    for center_bgr, count in zip(sorted_centers, sorted_counts):
        b, g, r = int(center_bgr[0]), int(center_bgr[1]), int(center_bgr[2])

        hex_color = "#{:02X}{:02X}{:02X}".format(r, g, b)

        hsv = cv2.cvtColor(
            np.uint8([[center_bgr.reshape(1, 3)]]),
            cv2.COLOR_BGR2HSV
        )[0][0]
        h, s, v = int(hsv[0]), int(hsv[1]), int(hsv[2])

        percentage = 100.0 * count / total_pixels

        colors.append({
            "bgr": (b, g, r),
            "hex": hex_color,
            "hsv": (h, s, v),
            "percentage": percentage
        })

    return colors


def save_roi_snapshot(roi_bgr, summary_text):
    """
    Save the ROI image and its summary text into a new folder under SAVED_ROI_ROOT.
    Folder is named based on current time in an ISO-8601-like format,
    but with ':' replaced to remain Windows-safe.
    """
    os.makedirs(SAVED_ROI_ROOT, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    folder = os.path.join(SAVED_ROI_ROOT, timestamp)
    os.makedirs(folder, exist_ok=True)

    img_path = os.path.join(folder, "roi.png")
    cv2.imwrite(img_path, roi_bgr)

    txt_path = os.path.join(folder, "summary.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"\n[Saved] ROI image:   {img_path}")
    print(f"[Saved] ROI summary: {txt_path}\n")


def build_summary_text(
    screen_w, screen_h,
    win_title, win_w, win_h,
    x_rel, y_rel, w_rel, h_rel,
    abs_left, abs_top, abs_right, abs_bottom,
    x_norm, y_norm, w_norm, h_norm,
    top_colors
):
    rel_top_left = (x_rel, y_rel)
    rel_top_right = (x_rel + w_rel, y_rel)
    rel_bottom_left = (x_rel, y_rel + h_rel)
    rel_bottom_right = (x_rel + w_rel, y_rel + h_rel)

    abs_top_left = (abs_left, abs_top)
    abs_top_right = (abs_right, abs_top)
    abs_bottom_left = (abs_left, abs_bottom)
    abs_bottom_right = (abs_right, abs_bottom)

    norm_top_left = (x_norm, y_norm)
    norm_top_right = (x_norm + w_norm, y_norm)
    norm_bottom_left = (x_norm, y_norm + h_norm)
    norm_bottom_right = (x_norm + w_norm, y_norm + h_norm)

    lines = []
    lines.append("===== ROI SUMMARY =====")
    lines.append(f"Monitor Resolution:             {screen_w} x {screen_h}")
    lines.append(f"Active Window Title:            {win_title}")
    lines.append(f"Active Window Size:             {win_w} x {win_h}")

    lines.append("")
    lines.append("ROI (Window-Relative):")
    lines.append(f"  Rectangle: x={x_rel}, y={y_rel}, w={w_rel}, h={h_rel}")
    lines.append("  Corners:")
    lines.append(f"    top-left     = {rel_top_left}")
    lines.append(f"    top-right    = {rel_top_right}")
    lines.append(f"    bottom-left  = {rel_bottom_left}")
    lines.append(f"    bottom-right = {rel_bottom_right}")

    lines.append("")
    lines.append("ROI (Absolute):")
    lines.append(f"  Rectangle: left={abs_left}, top={abs_top}, right={abs_right}, bottom={abs_bottom}")
    lines.append("  Corners:")
    lines.append(f"    top-left     = {abs_top_left}")
    lines.append(f"    top-right    = {abs_top_right}")
    lines.append(f"    bottom-left  = {abs_bottom_left}")
    lines.append(f"    bottom-right = {abs_bottom_right}")

    lines.append("")
    lines.append("ROI (Normalized to Window):")
    lines.append(f"  Rectangle: x={x_norm:.4f}, y={y_norm:.4f}, w={w_norm:.4f}, h={h_norm:.4f}")
    lines.append("  Corners:")
    lines.append(f"    top-left     = ({norm_top_left[0]:.4f}, {norm_top_left[1]:.4f})")
    lines.append(f"    top-right    = ({norm_top_right[0]:.4f}, {norm_top_right[1]:.4f})")
    lines.append(f"    bottom-left  = ({norm_bottom_left[0]:.4f}, {norm_bottom_left[1]:.4f})")
    lines.append(f"    bottom-right = ({norm_bottom_right[0]:.4f}, {norm_bottom_right[1]:.4f})")

    lines.append("")
    lines.append("Dominant Colors in ROI (K-Means):")
    if not top_colors:
        lines.append("  No pixels found in ROI.")
    else:
        for idx, c in enumerate(top_colors, start=1):
            hex_color = c["hex"]
            h, s, v = c["hsv"]
            pct = c["percentage"]
            lines.append(f"  {idx}. {hex_color} | HSV(OpenCV) = ({h}, {s}, {v}) | {pct:5.1f}%")

    lines.append("===== END OF ROI INFO =====")

    return "\n".join(lines)


def capture_window_and_select_roi(target_window=None):
    """
    Capture a given window (if target_window is provided) or the active window,
    let the user select an ROI, and save image + text summary.
    """
    window = target_window if target_window is not None else gw.getActiveWindow()
    if not window:
        print("No window detected.")
        return

    screen_w, screen_h = pyautogui.size()
    win_left = window.left
    win_top = window.top
    win_w = window.width
    win_h = window.height
    win_title = window.title

    screenshot = pyautogui.screenshot(region=(win_left, win_top, win_w, win_h))
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    x_rel, y_rel, w_rel, h_rel = cv2.selectROI("Select ROI", screenshot_cv, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow("Select ROI")

    if w_rel == 0 or h_rel == 0:
        print("ROI selection canceled or invalid.")
        return

    abs_left = win_left + x_rel
    abs_top = win_top + y_rel
    abs_right = abs_left + w_rel
    abs_bottom = abs_top + h_rel

    x_norm = x_rel / win_w
    y_norm = y_rel / win_h
    w_norm = w_rel / win_w
    h_norm = h_rel / win_h

    roi_bgr = screenshot_cv[y_rel:y_rel + h_rel, x_rel:x_rel + w_rel]
    top_colors = get_top_k_colors_kmeans(roi_bgr, k=3)

    summary_text = build_summary_text(
        screen_w, screen_h,
        win_title, win_w, win_h,
        x_rel, y_rel, w_rel, h_rel,
        abs_left, abs_top, abs_right, abs_bottom,
        x_norm, y_norm, w_norm, h_norm,
        top_colors
    )

    print("\n" + summary_text + "\n")
    save_roi_snapshot(roi_bgr, summary_text)


def wait_for_window_by_title(title, timeout=60.0, poll_interval=1.0):
    """
    Wait up to `timeout` seconds for a window whose title contains `title`
    (case-insensitive). Returns the window object or None.
    """
    title_lower = title.lower()
    end_time = time.time() + timeout

    while time.time() < end_time:
        windows = gw.getAllWindows()
        for w in windows:
            try:
                if w.title and title_lower in w.title.lower():
                    return w
            except Exception:
                # Some windows can be weird, skip them
                continue
        time.sleep(poll_interval)

    return None


def parse_args():
    parser = argparse.ArgumentParser(
        description="Capture ROI from a window and compute dominant colors."
    )
    parser.add_argument(
        "-c", "--continuous",
        action="store_true",
        help="Run in continuous mode (press 'o' to capture repeatedly, 'esc' to quit)."
    )
    parser.add_argument(
        "-t", "--title",
        type=str,
        help="Window title substring to search for (e.g. 'ARC Raiders'). "
             "If not provided, uses the active window."
    )
    return parser.parse_args()


def main():
    args = parse_args()

    continuous_mode = args.continuous
    title = args.title

    target_window = None

    if title:
        print(f"Searching for window with title containing '{title}' (up to 60 seconds)...")
        target_window = wait_for_window_by_title(title, timeout=60.0)
        if not target_window:
            print("Window not found within 60 seconds. Exiting.")
            return
        print(f"Found window: '{target_window.title}'")

    mode_str = "continuous" if continuous_mode else "single-run"
    print(f"Mode: {mode_str}")
    if title:
        print(f"Window source: title match -> '{title}'")
    else:
        print("Window source: active window")

    print(f"Press '{CAPTURE_KEY}' to capture the window and select ROI.")
    if continuous_mode:
        print("Press 'esc' to exit (continuous mode).")
    else:
        print("Script will exit after one ROI capture (single-run mode).")

    if continuous_mode:
        while True:
            if keyboard.is_pressed(CAPTURE_KEY):
                capture_window_and_select_roi(target_window)
                time.sleep(1)  # debouncing so holding the key doesn't spam
            if keyboard.is_pressed('esc'):
                print("Exiting (continuous mode).")
                break
            time.sleep(0.1)
    else:
        while True:
            if keyboard.is_pressed(CAPTURE_KEY):
                capture_window_and_select_roi(target_window)
                break
            time.sleep(0.1)


if __name__ == "__main__":
    main()
