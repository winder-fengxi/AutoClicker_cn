import tkinter as tk
from tkinter import ttk


def open_hotkey_settings_dialog(app) -> None:
    """打开快捷键设置窗口。"""
    top = tk.Toplevel(app.root)
    top.title(app.lang["hotkeys"])
    top.geometry("360x220")
    top.resizable(False, False)
    top.transient(app.root)
    top.grab_set()

    lbl_info = ttk.Label(top, text=app.lang.get("hotkey_hint", ""), wraplength=330)
    lbl_info.pack(pady=10)

    hotkey_frame = ttk.Frame(top)
    hotkey_frame.pack(fill=tk.X, padx=12, pady=8)

    lbl_start = ttk.Label(
        hotkey_frame,
        text=f"{app.lang.get('hotkey_start_label', '')}: {app.hotkey_start_var.get()}",
        font=("Arial", 10, "bold"),
    )
    lbl_start.grid(row=0, column=0, sticky="w", pady=6)
    btn_start = ttk.Button(hotkey_frame, text=app.lang.get("set_start", ""), width=10)
    btn_start.grid(row=0, column=1, padx=8)

    lbl_stop = ttk.Label(
        hotkey_frame,
        text=f"{app.lang.get('hotkey_stop_label', '')}: {app.hotkey_stop_var.get()}",
        font=("Arial", 10, "bold"),
    )
    lbl_stop.grid(row=1, column=0, sticky="w", pady=6)
    btn_stop = ttk.Button(hotkey_frame, text=app.lang.get("set_stop", ""), width=10)
    btn_stop.grid(row=1, column=1, padx=8)

    pending_target = {"value": None}

    def normalize_key(raw_key):
        if not raw_key or raw_key == "??":
            return None
        if raw_key.lower() in ["shift_l", "shift_r", "control_l", "control_r", "alt_l", "alt_r"]:
            return None
        return raw_key.upper() if len(raw_key) > 1 else raw_key.lower()

    def begin_capture(target):
        pending_target["value"] = target
        if target == "start":
            lbl_info.config(text=app.lang.get("press_start_key", ""))
        else:
            lbl_info.config(text=app.lang.get("press_stop_key", ""))
        top.focus_set()

    def on_key_press(event):
        if pending_target["value"] is None:
            return
        new_key = normalize_key(event.keysym)
        if new_key is None:
            return

        if pending_target["value"] == "start":
            app.hotkey_start_var.set(new_key)
            lbl_start.config(text=f"{app.lang.get('hotkey_start_label', '')}: {new_key}")
        else:
            app.hotkey_stop_var.set(new_key)
            lbl_stop.config(text=f"{app.lang.get('hotkey_stop_label', '')}: {new_key}")

        pending_target["value"] = None
        app.save_settings()
        app.start_hotkey_listener()
        app.refresh_hotkey_button_texts()
        lbl_info.config(text=app.lang.get("hotkey_updated", ""))

    btn_start.config(command=lambda: begin_capture("start"))
    btn_stop.config(command=lambda: begin_capture("stop"))

    top.bind("<Key>", on_key_press)
    top.focus_set()
