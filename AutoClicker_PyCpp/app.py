import os
import tkinter as tk
from typing import Any
from tkinter import messagebox
from pynput import keyboard, mouse

from clicker_service import ClickerService
from config_service import load_languages, load_settings, save_settings
from hotkey_dialog import open_hotkey_settings_dialog
from ui_builder import build_main_ui


class AutoClickerApp:
    def __init__(self, root):
        """
        功能: 初始化应用程序，加载配置，构建 UI，启动监听器
        输入参数: root (Tkinter 主窗口对象)
        输出结果: 无
        变量名: root, self.languages, self.current_lang
        """
        self.root = root
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.languages = load_languages(self.base_dir)
        self.current_lang = "zh_cn"
        self.lang = self.languages.get(self.current_lang, self.languages.get("en", {"title": "AutoClicker"}))

        self.root.title(self.lang["title"])
        self.root.geometry("450x450")
        self.root.resizable(False, False)

        self.clicker_service = ClickerService(self.base_dir)

        self.hours_var = tk.StringVar(value="0")
        self.mins_var = tk.StringVar(value="0")
        self.secs_var = tk.StringVar(value="0")
        self.millis_var = tk.StringVar(value="100")

        self.button_var = tk.StringVar(value="Left")
        self.click_type_var = tk.StringVar(value="Single")
        self.repeat_mode_var = tk.StringVar(value="Infinite")
        self.repeat_count_var = tk.StringVar(value="100")
        self.location_mode_var = tk.StringVar(value="Current")
        self.picked_x_var = tk.StringVar(value="0")
        self.picked_y_var = tk.StringVar(value="0")
        self.status_var = tk.StringVar(value=self.lang["stopped"])
        self.hotkey_start_var = tk.StringVar(value="F6")
        self.hotkey_stop_var = tk.StringVar(value="F7")
        self.chk_top_var = tk.IntVar(value=0)

        self.lbl_status = None
        self.is_running = False
        self.is_picking = False
        self.listener = None
        self.mouse_listener = None

        self.lbl_language: Any = None
        self.group_interval: Any = None
        self.lbl_hours: Any = None
        self.lbl_mins: Any = None
        self.lbl_secs: Any = None
        self.lbl_millis: Any = None
        self.group_repeat: Any = None
        self.rb_repeat_inf: Any = None
        self.rb_repeat_count: Any = None
        self.lbl_times: Any = None
        self.group_pos: Any = None
        self.rb_pos_current: Any = None
        self.rb_pos_picked: Any = None
        self.btn_pick: Any = None
        self.group_mouse: Any = None
        self.lbl_mouse_btn: Any = None
        self.lbl_click_type: Any = None
        self.combo_btn: Any = None
        self.combo_type: Any = None
        self.btn_start: Any = None
        self.btn_stop: Any = None
        self.btn_save: Any = None
        self.btn_hotkeys: Any = None
        self.chk_top: Any = None

        self.load_settings()
        build_main_ui(self)
        self.start_hotkey_listener()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_settings(self):
        """
        功能: 从 settings.json 文件加载保存的配置
        输入参数: 无
        输出结果: 无
        变量名: settings
        """
        settings = load_settings(self.base_dir)
        if not settings:
            return

        self.hours_var.set(settings.get("hours", "0"))
        self.mins_var.set(settings.get("mins", "0"))
        self.secs_var.set(settings.get("secs", "0"))
        self.millis_var.set(settings.get("millis", "100"))
        self.button_var.set(settings.get("button", "Left"))
        self.click_type_var.set(settings.get("click_type", "Single"))
        self.repeat_mode_var.set(settings.get("repeat_mode", "Infinite"))
        self.repeat_count_var.set(settings.get("repeat_count", "100"))
        self.location_mode_var.set(settings.get("location_mode", "Current"))
        self.picked_x_var.set(settings.get("x", "0"))
        self.picked_y_var.set(settings.get("y", "0"))
        self.chk_top_var.set(settings.get("top_most", 0))

        saved_lang = settings.get("language", "zh_cn")
        if saved_lang in self.languages:
            self.current_lang = saved_lang
            self.lang = self.languages[self.current_lang]

        self.hotkey_start_var.set(settings.get("hotkey_start", "F6"))
        self.hotkey_stop_var.set(settings.get("hotkey_stop", "F7"))

    def _hotkey_display_text(self, hotkey: str) -> str:
        """
        功能: 生成用于界面显示的快捷键文本
        输入参数: hotkey (快捷键字符串)
        输出结果: str (格式化后的快捷键文本)
        变量名: hotkey
        """
        if not hotkey:
            return ""
        return hotkey.upper()

    def get_start_button_text(self) -> str:
        """
        功能: 生成开始按钮文本（包含快捷键）
        输入参数: 无
        输出结果: str (按钮显示文本)
        变量名: base_text, hotkey_text
        """
        base_text = self.lang["start"]
        hotkey_text = self._hotkey_display_text(self.hotkey_start_var.get())
        return f"{base_text} ({hotkey_text})" if hotkey_text else base_text

    def get_stop_button_text(self) -> str:
        """
        功能: 生成停止按钮文本（包含快捷键）
        输入参数: 无
        输出结果: str (按钮显示文本)
        变量名: base_text, hotkey_text
        """
        base_text = self.lang["stop"]
        hotkey_text = self._hotkey_display_text(self.hotkey_stop_var.get())
        return f"{base_text} ({hotkey_text})" if hotkey_text else base_text

    def refresh_hotkey_button_texts(self):
        """
        功能: 刷新开始/停止按钮文本中的快捷键信息
        输入参数: 无
        输出结果: 无
        变量名: self.btn_start, self.btn_stop
        """
        if self.btn_start:
            self.btn_start.config(text=self.get_start_button_text())
        if self.btn_stop:
            self.btn_stop.config(text=self.get_stop_button_text())

    def update_ui_text(self):
        """
        功能: 根据当前选择的语言刷新所有界面文本
        输入参数: 无
        输出结果: 无
        变量名: self.lang, set_text
        """
        self.lang = self.languages[self.current_lang]
        self.root.title(self.lang["title"])

        def set_text(widget, key):
            if widget:
                widget.config(text=self.lang[key])

        if hasattr(self, "group_interval"):
            self.group_interval.config(text=self.lang["click_interval"])
        set_text(self.lbl_hours, "hours")
        set_text(self.lbl_mins, "mins")
        set_text(self.lbl_secs, "secs")
        set_text(self.lbl_millis, "millis")

        if hasattr(self, "group_repeat"):
            self.group_repeat.config(text=self.lang["click_repeat"])
        set_text(self.rb_repeat_inf, "repeat_until_stopped")
        set_text(self.lbl_times, "times")

        if hasattr(self, "group_pos"):
            self.group_pos.config(text=self.lang["cursor_position"])
        set_text(self.rb_pos_current, "current_location")
        set_text(self.rb_pos_picked, "pick_location")

        if hasattr(self, "group_mouse"):
            self.group_mouse.config(text=self.lang["mouse_options"])
        set_text(self.lbl_mouse_btn, "mouse_button")
        set_text(self.lbl_click_type, "click_type")

        if hasattr(self, "combo_btn"):
            self.combo_btn["values"] = [self.lang["left"], self.lang["right"], self.lang["middle"]]
            current_btn_idx = {"Left": 0, "Right": 1, "Middle": 2}.get(self.button_var.get(), 0)
            self.combo_btn.current(current_btn_idx)

        if hasattr(self, "combo_type"):
            self.combo_type["values"] = [self.lang["single"], self.lang["double"]]
            current_type_idx = {"Single": 0, "Double": 1}.get(self.click_type_var.get(), 0)
            self.combo_type.current(current_type_idx)

        self.refresh_hotkey_button_texts()
        if hasattr(self, "btn_save"):
            self.btn_save.config(text=self.lang["save_settings"])
        if hasattr(self, "btn_hotkeys"):
            self.btn_hotkeys.config(text=self.lang["hotkeys"])
        if hasattr(self, "chk_top"):
            self.chk_top.config(text=self.lang["top_most"])
        if hasattr(self, "lbl_language"):
            self.lbl_language.config(text=self.lang["language_label"])

        self.update_status(self.is_running)

    def change_language(self, lang_code):
        """
        功能: 切换应用程序语言并更新 UI
        输入参数: lang_code (语言代码)
        输出结果: 无
        变量名: self.current_lang
        """
        self.current_lang = lang_code
        self.update_ui_text()

    def on_combo_change(self, event):
        """
        功能: 下拉框变化事件，同步界面选择到内部配置变量
        输入参数: event (Tkinter 事件对象)
        输出结果: 无
        变量名: event, btn_idx, type_idx
        """
        btn_idx = self.combo_btn.current()
        if btn_idx == 0:
            self.button_var.set("Left")
        elif btn_idx == 1:
            self.button_var.set("Right")
        elif btn_idx == 2:
            self.button_var.set("Middle")

        type_idx = self.combo_type.current()
        if type_idx == 0:
            self.click_type_var.set("Single")
        elif type_idx == 1:
            self.click_type_var.set("Double")

    def toggle_top_window(self):
        """
        功能: 切换主窗口置顶状态
        输入参数: 无
        输出结果: 无
        变量名: self.chk_top_var
        """
        self.root.attributes("-topmost", self.chk_top_var.get())

    def start_pick_location(self):
        """
        功能: 启动坐标拾取模式并监听下一次鼠标点击
        输入参数: 无
        输出结果: 无
        变量名: self.is_picking, self.mouse_listener
        """
        if self.is_picking:
            return
        self.is_picking = True
        self.root.config(cursor="cross")
        self.btn_pick.config(state="disabled")
        self.mouse_listener = mouse.Listener(on_click=self.on_pick_click)
        self.mouse_listener.start()

    def on_pick_click(self, x, y, button, pressed):
        """
        功能: 鼠标点击回调，捕获坐标并结束拾取
        输入参数: x, y, button, pressed
        输出结果: False (命中后停止监听) 或 None
        变量名: x, y, button, pressed
        """
        if pressed and self.is_picking:
            self.root.after(0, lambda: self.finish_pick(x, y))
            return False

    def finish_pick(self, x, y):
        """
        功能: 写入拾取坐标并恢复 UI 状态
        输入参数: x, y (拾取到的坐标)
        输出结果: 无
        变量名: self.picked_x_var, self.picked_y_var
        """
        self.picked_x_var.set(str(int(x)))
        self.picked_y_var.set(str(int(y)))
        self.location_mode_var.set("Picked")
        self.is_picking = False
        self.root.config(cursor="")
        self.btn_pick.config(state="normal")

    def save_settings(self):
        """
        功能: 将当前配置保存到 settings.json
        输入参数: 无
        输出结果: 无
        变量名: settings
        """
        settings = {
            "hours": self.hours_var.get(),
            "mins": self.mins_var.get(),
            "secs": self.secs_var.get(),
            "millis": self.millis_var.get(),
            "button": self.button_var.get(),
            "click_type": self.click_type_var.get(),
            "repeat_mode": self.repeat_mode_var.get(),
            "repeat_count": self.repeat_count_var.get(),
            "location_mode": self.location_mode_var.get(),
            "x": self.picked_x_var.get(),
            "y": self.picked_y_var.get(),
            "top_most": self.chk_top_var.get(),
            "language": self.current_lang,
            "hotkey_start": self.hotkey_start_var.get(),
            "hotkey_stop": self.hotkey_stop_var.get(),
        }
        try:
            save_settings(self.base_dir, settings)
            messagebox.showinfo(self.lang["title"], self.lang["settings_saved"])
        except Exception as error:
            messagebox.showerror(self.lang["error_title"], str(error))

    def open_hotkey_settings(self):
        """
        功能: 打开快捷键设置窗口并更新快捷键监听
        输入参数: 无
        输出结果: 无
        变量名: 无
        """
        open_hotkey_settings_dialog(self)

    def start_hotkey_listener(self):
        """
        功能: 启动全局快捷键监听
        输入参数: 无
        输出结果: 无
        变量名: start_hotkey, stop_hotkey, hotkey_map, self.listener
        """
        start_hotkey = self.hotkey_start_var.get()
        stop_hotkey = self.hotkey_stop_var.get()

        if self.listener is not None:
            try:
                self.listener.stop()
            except Exception:
                pass
            self.listener = None

        def to_key_map(hotkey_value):
            if not hotkey_value:
                return None
            return f"<{hotkey_value.lower()}>" if len(hotkey_value) > 1 else hotkey_value.lower()

        start_key_map = to_key_map(start_hotkey)
        stop_key_map = to_key_map(stop_hotkey)

        hotkey_map = {}
        if start_key_map and stop_key_map and start_key_map == stop_key_map:
            hotkey_map[start_key_map] = self.toggle_clicking
        else:
            if start_key_map:
                hotkey_map[start_key_map] = self.on_start_hotkey
            if stop_key_map:
                hotkey_map[stop_key_map] = self.on_stop_hotkey

        if not hotkey_map:
            return

        try:
            self.listener = keyboard.GlobalHotKeys(hotkey_map)
            self.listener.start()
            print(f"Hotkey listener started: {list(hotkey_map.keys())}")
        except Exception as error:
            print(f"Failed to start hotkey listener: {error}")

    def on_start_hotkey(self):
        """
        功能: 开始快捷键回调，仅在停止状态下启动点击
        输入参数: 无
        输出结果: 无
        变量名: self.is_running
        """
        if not self.is_running:
            self.root.after(0, self.start_clicking)

    def on_stop_hotkey(self):
        """
        功能: 停止快捷键回调，仅在运行状态下停止点击
        输入参数: 无
        输出结果: 无
        变量名: self.is_running
        """
        if self.is_running:
            self.root.after(0, self.stop_clicking)

    def toggle_clicking(self):
        """
        功能: 快捷键触发开始/停止切换 (线程安全)
        输入参数: 无
        输出结果: 无
        变量名: self.is_running
        """
        if self.is_running:
            self.root.after(0, self.stop_clicking)
        else:
            self.root.after(0, self.start_clicking)

    def calculate_interval(self):
        """
        功能: 计算点击间隔总毫秒数
        输入参数: 无
        输出结果: int (毫秒) 或 None (输入错误)
        变量名: h, m, s, ms, total
        """
        try:
            h = int(self.hours_var.get()) if self.hours_var.get() else 0
            m = int(self.mins_var.get()) if self.mins_var.get() else 0
            s = int(self.secs_var.get()) if self.secs_var.get() else 0
            ms = int(self.millis_var.get()) if self.millis_var.get() else 0
            total = (h * 3600 * 1000) + (m * 60 * 1000) + (s * 1000) + ms
            return max(1, total)
        except ValueError:
            messagebox.showerror(self.lang["error_title"], self.lang["invalid_time_interval"])
            return None

    def start_clicking(self):
        """
        功能: 收集参数并调用 C++ 启动点击器
        输入参数: 无
        输出结果: 无
        变量名: interval, btn_idx, type_idx, loop_mode, loop_count, loc_mode, fixed_x, fixed_y
        """
        if not self.clicker_service.available or self.is_running:
            return

        interval = self.calculate_interval()
        if interval is None:
            return

        btn_idx = self.combo_btn.current()
        if btn_idx == -1:
            btn_idx = 0

        type_idx = self.combo_type.current()
        if type_idx == -1:
            type_idx = 0

        loop_mode = 0
        loop_count = 0
        if self.repeat_mode_var.get() == "Count":
            loop_mode = 1
            try:
                loop_count = int(self.repeat_count_var.get())
            except ValueError:
                loop_count = 100

        loc_mode = 0
        fixed_x = 0
        fixed_y = 0
        if self.location_mode_var.get() == "Picked":
            loc_mode = 1
            try:
                fixed_x = int(self.picked_x_var.get())
                fixed_y = int(self.picked_y_var.get())
            except ValueError:
                fixed_x = 0
                fixed_y = 0

        self.clicker_service.start(interval, btn_idx, loop_mode, loop_count, loc_mode, fixed_x, fixed_y, type_idx)
        self.is_running = True
        self.update_status(True)

    def stop_clicking(self):
        """
        功能: 调用 C++ 停止点击器
        输入参数: 无
        输出结果: 无
        变量名: self.is_running
        """
        if not self.is_running:
            return
        self.clicker_service.stop()
        self.is_running = False
        self.update_status(False)

    def update_status(self, running):
        """
        功能: 刷新状态文本和按钮状态
        输入参数: running (bool)
        输出结果: 无
        变量名: self.status_var, self.lbl_status
        """
        if not self.lbl_status:
            return

        if running:
            self.status_var.set(self.lang["running"])
            self.lbl_status.config(fg="green")
            self.btn_start.config(state="disabled")
        else:
            self.status_var.set(self.lang["stopped"])
            self.lbl_status.config(fg="red")
            self.btn_start.config(state="normal")

    def on_close(self):
        """
        功能: 关闭窗口前执行资源清理
        输入参数: 无
        输出结果: 无
        变量名: self.listener, self.mouse_listener
        """
        if self.is_running:
            self.stop_clicking()
        if self.listener:
            self.listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
