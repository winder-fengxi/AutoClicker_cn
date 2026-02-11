import ctypes
import os
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pynput import keyboard, mouse  # 导入 pynput 用于监听键盘热键和鼠标事件

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        
        # 1. 加载语言配置
        self.load_languages()
        
        # 设置默认语言 ( zh_cn )
        self.current_lang = "zh_cn" 
        self.lang = self.languages[self.current_lang]

        # 设置窗口标题和大小
        self.root.title(self.lang["title"])
        self.root.geometry("450x450")
        self.root.resizable(False, False)

        # 2. 加载 C++ DLL 核心库
        self.load_dll()

        # 3. 初始化 UI 变量 (Tkinter StringVars)
        # 点击间隔变量 (时/分/秒/毫秒)
        self.hours_var = tk.StringVar(value="0")
        self.mins_var = tk.StringVar(value="0")
        self.secs_var = tk.StringVar(value="0")
        self.millis_var = tk.StringVar(value="100")

        # 鼠标选项变量
        self.button_var = tk.StringVar(value="Left") # Left(左键), Right, Middle
        self.click_type_var = tk.StringVar(value="Single") # Single(单击), Double
        
        # 重复模式变量
        self.repeat_mode_var = tk.StringVar(value="Infinite") # Infinite(无限), Count(次数)
        self.repeat_count_var = tk.StringVar(value="100")
        
        # 位置模式选项
        self.location_mode_var = tk.StringVar(value="Current") # Current(当前位置), Picked(指定位置)
        self.picked_x_var = tk.StringVar(value="0")
        self.picked_y_var = tk.StringVar(value="0")

        # 状态栏变量
        self.status_var = tk.StringVar(value=self.lang["stopped"])
        self.hotkey_var = tk.StringVar(value="F6")
        
        self.lbl_status = None

        # 运行状态标志
        self.is_running = False
        self.is_picking = False
        self.listener = None       # 键盘监听器对象
        self.mouse_listener = None # 鼠标监听器对象

        # 4. 构建 UI 界面
        self.build_ui()

        # 5. 启动热键监听 (F6)
        self.start_hotkey_listener()

        # 处理窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_languages(self):
        """ 加载 languages.json 文件 """
        try:
            lang_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "languages.json")
            with open(lang_path, "r", encoding="utf-8") as f:
                self.languages = json.load(f)
        except Exception as e:
            # 加载失败时的回退默认值
            # Fallback
            self.languages = {"en": {"title": "AutoClicker"}} 
            print(f"Error loading languages: {e}")

    def update_ui_text(self):
        """ 切换语言时更新所有 UI 文本 """
        self.lang = self.languages[self.current_lang]
        self.root.title(self.lang["title"])
        
        # 辅助函数：更新 Label 文本
        def set_text(widget, key):
            if widget: widget.config(text=self.lang[key])

        # 更新：点击间隔区域
        if hasattr(self, 'group_interval'): self.group_interval.config(text=self.lang["click_interval"])
        set_text(self.lbl_hours, "hours")
        set_text(self.lbl_mins, "mins")
        set_text(self.lbl_secs, "secs")
        set_text(self.lbl_millis, "millis")

        # 更新：重复模式区域
        if hasattr(self, 'group_repeat'): self.group_repeat.config(text=self.lang["click_repeat"])
        set_text(self.rb_repeat_inf, "repeat_until_stopped")
        set_text(self.lbl_times, "times")
        
        # 更新：位置区域
        if hasattr(self, 'group_pos'): self.group_pos.config(text=self.lang["cursor_position"])
        set_text(self.rb_pos_current, "current_location")
        set_text(self.rb_pos_picked, "pick_location")

        # 更新：鼠标选项区域
        if hasattr(self, 'group_mouse'): self.group_mouse.config(text=self.lang["mouse_options"])
        set_text(self.lbl_mouse_btn, "mouse_button")
        set_text(self.lbl_click_type, "click_type")
        
        # 更新：下拉框选项 (需要重新设置 values)
        if hasattr(self, 'combo_btn'):
            self.combo_btn['values'] = [self.lang["left"], self.lang["right"], self.lang["middle"]]
            # 重新选中当前项以更新显示文本
            current_btn_idx = {"Left": 0, "Right": 1, "Middle": 2}.get(self.button_var.get(), 0)
            self.combo_btn.current(current_btn_idx)

        if hasattr(self, 'combo_type'):
            self.combo_type['values'] = [self.lang["single"], self.lang["double"]]
            current_type_idx = {"Single": 0, "Double": 1}.get(self.click_type_var.get(), 0)
            self.combo_type.current(current_type_idx)

        # 更新：底部按钮
        if hasattr(self, 'btn_start'): self.btn_start.config(text=self.lang["start"])
        if hasattr(self, 'btn_stop'): self.btn_stop.config(text=self.lang["stop"])
        if hasattr(self, 'btn_save'): self.btn_save.config(text=self.lang["save_settings"])
        if hasattr(self, 'btn_hotkeys'): self.btn_hotkeys.config(text=self.lang["hotkeys"])
        if hasattr(self, 'chk_top'): self.chk_top.config(text=self.lang["top_most"])
        
        # 更新状态文本
        self.update_status(self.is_running)

    def change_language(self, lang_code):
        """ 切换当前语言 """
        self.current_lang = lang_code
        self.update_ui_text()

    def build_ui(self):
        """ 构建 Tkinter 界面组件 """
        main_pad = 5
        
        # --- 顶部：语言切换 ---
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X)
        
        lang_frame = ttk.Frame(top_frame)
        lang_frame.pack(side=tk.RIGHT, padx=5)
        ttk.Label(lang_frame, text="Language: ").pack(side=tk.LEFT)
        combo_lang = ttk.Combobox(lang_frame, values=["zh_cn", "en"], state="readonly", width=8)
        combo_lang.set(self.current_lang)
        combo_lang.pack(side=tk.LEFT)
        combo_lang.bind("<<ComboboxSelected>>", lambda e: self.change_language(combo_lang.get()))


        # --- 分组1：点击间隔 (Click Interval) ---
        self.group_interval = ttk.LabelFrame(self.root, text=self.lang["click_interval"], padding=10)
        self.group_interval.pack(fill=tk.X, padx=main_pad, pady=5)
        
        int_frame = ttk.Frame(self.group_interval)
        int_frame.pack(fill=tk.X)
        
        def create_time_entry(parent, var, label_key):
            f = ttk.Frame(parent)
            f.pack(side=tk.LEFT, padx=5, expand=True)
            e = ttk.Entry(f, textvariable=var, width=5)
            e.pack(side=tk.LEFT)
            l = ttk.Label(f, text=self.lang[label_key])
            l.pack(side=tk.LEFT, padx=2)
            return l

        self.lbl_hours = create_time_entry(int_frame, self.hours_var, "hours")
        self.lbl_mins = create_time_entry(int_frame, self.mins_var, "mins")
        self.lbl_secs = create_time_entry(int_frame, self.secs_var, "secs")
        self.lbl_millis = create_time_entry(int_frame, self.millis_var, "millis")


        # --- 中间部分 (左右分栏) ---
        mid_frame = ttk.Frame(self.root)
        mid_frame.pack(fill=tk.X, padx=main_pad, pady=5)
        
        # 分组2 (左): 重复模式 (Click Repeat)
        self.group_repeat = ttk.LabelFrame(mid_frame, text=self.lang["click_repeat"], padding=10)
        self.group_repeat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.rb_repeat_inf = ttk.Radiobutton(self.group_repeat, text=self.lang["repeat_until_stopped"], variable=self.repeat_mode_var, value="Infinite")
        self.rb_repeat_inf.pack(anchor=tk.W, pady=2)
        
        repeat_cnt_frame = ttk.Frame(self.group_repeat)
        repeat_cnt_frame.pack(anchor=tk.W, pady=2)
        self.rb_repeat_count = ttk.Radiobutton(repeat_cnt_frame, text="", variable=self.repeat_mode_var, value="Count")
        self.rb_repeat_count.pack(side=tk.LEFT)
        ttk.Entry(repeat_cnt_frame, textvariable=self.repeat_count_var, width=6).pack(side=tk.LEFT, padx=5)
        self.lbl_times = ttk.Label(repeat_cnt_frame, text=self.lang["times"])
        self.lbl_times.pack(side=tk.LEFT)


        # 分组3 (右): 光标位置 (Click Position)
        self.group_pos = ttk.LabelFrame(mid_frame, text=self.lang["cursor_position"], padding=10)
        self.group_pos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.rb_pos_current = ttk.Radiobutton(self.group_pos, text=self.lang["current_location"], variable=self.location_mode_var, value="Current")
        self.rb_pos_current.pack(anchor=tk.W, pady=2)

        pos_pick_frame = ttk.Frame(self.group_pos)
        pos_pick_frame.pack(anchor=tk.W, pady=2)
        self.rb_pos_picked = ttk.Radiobutton(pos_pick_frame, text="", variable=self.location_mode_var, value="Picked")
        self.rb_pos_picked.pack(side=tk.LEFT)
        
        ttk.Label(pos_pick_frame, text="X").pack(side=tk.LEFT, padx=2)
        ttk.Entry(pos_pick_frame, textvariable=self.picked_x_var, width=4).pack(side=tk.LEFT)
        ttk.Label(pos_pick_frame, text="Y").pack(side=tk.LEFT, padx=2)
        ttk.Entry(pos_pick_frame, textvariable=self.picked_y_var, width=4).pack(side=tk.LEFT)
        
        self.btn_pick = ttk.Button(pos_pick_frame, text="🎯", width=3, command=self.start_pick_location)
        self.btn_pick.pack(side=tk.LEFT, padx=5)


        # --- 分组4：鼠标选项 (Click Options) ---
        self.group_mouse = ttk.LabelFrame(self.root, text=self.lang["mouse_options"], padding=10)
        self.group_mouse.pack(fill=tk.X, padx=main_pad, pady=5)
        
        opts_frame = ttk.Frame(self.group_mouse)
        opts_frame.pack(fill=tk.X)
        
        # 子项1: 鼠标按键 (左/中/右)
        self.lbl_mouse_btn = ttk.Label(opts_frame, text=self.lang["mouse_button"])
        self.lbl_mouse_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.combo_btn = ttk.Combobox(opts_frame, state="readonly", width=10)
        self.combo_btn['values'] = [self.lang["left"], self.lang["right"], self.lang["middle"]]
        self.combo_btn.current(0)
        self.combo_btn.pack(side=tk.LEFT, padx=(0, 20))
        self.combo_btn.bind("<<ComboboxSelected>>", self.on_combo_change)

        # 子项2: 点击类型 (单击/双击)
        self.lbl_click_type = ttk.Label(opts_frame, text=self.lang["click_type"])
        self.lbl_click_type.pack(side=tk.LEFT, padx=(0, 5))
        
        self.combo_type = ttk.Combobox(opts_frame, state="readonly", width=10)
        self.combo_type['values'] = [self.lang["single"], self.lang["double"]]
        self.combo_type.current(0)
        self.combo_type.pack(side=tk.LEFT)
        self.combo_type.bind("<<ComboboxSelected>>", self.on_combo_change)


        # --- 底部按钮区域 ---
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=main_pad, pady=10)

        # 第一排: 开始, 停止
        b_row1 = ttk.Frame(btn_frame)
        b_row1.pack(fill=tk.X, pady=2)
        
        self.btn_start = ttk.Button(b_row1, text=self.lang["start"], command=self.start_clicking)
        self.btn_start.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.btn_stop = ttk.Button(b_row1, text=self.lang["stop"], command=self.stop_clicking)
        self.btn_stop.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # 第二排: 保存, 热键, 置顶
        b_row2 = ttk.Frame(btn_frame)
        b_row2.pack(fill=tk.X, pady=5)

        self.btn_save = ttk.Button(b_row2, text=self.lang["save_settings"], command=self.save_settings)
        self.btn_save.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.btn_hotkeys = ttk.Button(b_row2, text=self.lang["hotkeys"], command=self.open_hotkey_settings)
        self.btn_hotkeys.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.chk_top_var = tk.IntVar()
        self.chk_top = ttk.Checkbutton(b_row2, text=self.lang["top_most"], variable=self.chk_top_var, command=self.toggle_top_window)
        self.chk_top.pack(side=tk.RIGHT, padx=5)

        # 状态标签
        self.lbl_status = tk.Label(self.root, textvariable=self.status_var, font=("Arial", 10, "bold"), fg="red")
        self.lbl_status.pack(pady=5)

        if self.clicker_lib is None:
             tk.Label(self.root, text=self.lang["error_dll"], fg="red").pack()

    def on_combo_change(self, event):
        """ 下拉框变更事件 (保留接口，目前不需要特殊处理) """
        pass

    def toggle_top_window(self):
        """ 切换窗口置顶状态 """
        self.root.attributes("-topmost", self.chk_top_var.get())

    def start_pick_location(self):
        """ 开始拾取坐标流程 """
        if self.is_picking: return
        self.is_picking = True
        self.root.config(cursor="cross") # 更改鼠标样式为十字
        self.btn_pick.config(state="disabled")
        
        # 启动鼠标监听器，只监听一次点击
        # 注意: pynput listener 在独立线程运行
        self.mouse_listener = mouse.Listener(on_click=self.on_pick_click)
        self.mouse_listener.start()

    def on_pick_click(self, x, y, button, pressed):
        """ 鼠标点击回调 (在 pynput 线程中运行) """
        if pressed and self.is_picking:
            # 使用 root.after 将 UI 更新操作调度回主线程
            self.root.after(0, lambda: self.finish_pick(x, y))
            # 返回 False 以停止监听器
            return False 

    def finish_pick(self, x, y):
        """ 拾取完成，更新 UI """
        self.picked_x_var.set(str(int(x)))
        self.picked_y_var.set(str(int(y)))
        self.location_mode_var.set("Picked") # 自动切换到指定模式
        self.is_picking = False
        self.root.config(cursor="") # 恢复鼠标样式
        self.btn_pick.config(state="normal")

    def save_settings(self):
        """ 保存当前设置到 settings.json """
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
            "language": self.current_lang
        }
        try:
            settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
            with open(settings_path, "w", encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            messagebox.showinfo(self.lang["server_title"] if "server_title" in self.lang else "AutoClicker", "Settings Saved!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_hotkey_settings(self):
        """ 显示热键提示 """
        messagebox.showinfo(self.lang["hotkeys"], "Hotkeys:\nStart/Stop: F6")


    def load_dll(self):
        """ 加载 clicker_core.dll 并定义函数签名 """
        try:
            # 假设 DLL 在同级目录
            dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clicker_core.dll")
            if not os.path.exists(dll_path):
                # Fallback
                pass 
            
            self.clicker_lib = ctypes.CDLL(dll_path)
            
            # 定义 StartClicker 参数类型: interval, btn_code, loopMode, loopCount, locationMode, fixedX, fixedY, doubleClick
            self.clicker_lib.StartClicker.argtypes = [
                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int
            ]
            self.clicker_lib.StartClicker.restype = None
            
            # 定义 StopClicker
            self.clicker_lib.StopClicker.argtypes = []
            self.clicker_lib.StopClicker.restype = None
            
            # 定义 IsRunning
            self.clicker_lib.IsRunning.argtypes = []
            self.clicker_lib.IsRunning.restype = ctypes.c_bool
            
        except Exception as e:
            print(f"Failed to load DLL: {e}")
            self.clicker_lib = None


    def start_hotkey_listener(self):
        """ 启动全局键盘监听 (F6) """
        self.listener = keyboard.GlobalHotKeys({'<f6>': self.toggle_clicking})
        self.listener.start()

    def toggle_clicking(self):
        """ 热键回调: 切换开始/停止 """
        if self.is_running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def calculate_interval(self):
        """ 计算总毫秒数 """
        try:
            h = int(self.hours_var.get())
            m = int(self.mins_var.get())
            s = int(self.secs_var.get())
            ms = int(self.millis_var.get())
            total = (h * 3600 * 1000) + (m * 60 * 1000) + (s * 1000) + ms
            return max(1, total) # 最小间隔 1ms
        except:
            return 100

    def start_clicking(self):
        """ 收集参数并调用 C++ 开始点击 """
        if self.clicker_lib is None or self.is_running:
            return

        interval = self.calculate_interval()
        
        # 鼠标按键 (从 Combobox 索引获取)
        btn_idx = self.combo_btn.current()
        if btn_idx == -1: btn_idx = 0 # 默认为左键
        
        # 点击类型 (从 Combobox 索引获取)
        type_idx = self.combo_type.current() # 0=单击, 1=双击
        if type_idx == -1: type_idx = 0

        # 循环模式
        loop_mode = 0 # Infinite
        loop_count = 0
        if self.repeat_mode_var.get() == "Count":
            loop_mode = 1
            try:
                loop_count = int(self.repeat_count_var.get())
            except:
                loop_count = 100

        # 位置模式
        loc_mode = 0 # Current
        fixed_x = 0
        fixed_y = 0
        if self.location_mode_var.get() == "Picked":
            loc_mode = 1
            try:
                 fixed_x = int(self.picked_x_var.get())
                 fixed_y = int(self.picked_y_var.get())
            except:
                 fixed_x = 0
                 fixed_y = 0
        
        # 调用 C++ 函数
        self.clicker_lib.StartClicker(
            interval, 
            btn_idx, 
            loop_mode, 
            loop_count, 
            loc_mode, 
            fixed_x, 
            fixed_y, 
            type_idx
        )
        
        self.is_running = True
        self.update_status(True)

    def stop_clicking(self):
        """ 调用 C++ 停止点击 """
        if self.clicker_lib is None or not self.is_running:
            return

        # 调用 C++
        self.clicker_lib.StopClicker()
        
        self.is_running = False
        self.update_status(False)

    def update_status(self, running):
        """ 更新界面状态显示 """
        if not self.lbl_status: return
        
        if running:
            self.status_var.set(self.lang["running"])
            self.lbl_status.config(fg="green")
            self.btn_start.config(state="disabled") # 运行时禁用开始按钮
        else:
            self.status_var.set(self.lang["stopped"])
            self.lbl_status.config(fg="red")
            self.btn_start.config(state="normal")

    def on_close(self):
        """ 程序关闭清理 """
        if self.is_running:
            self.stop_clicking()
        if self.listener:
            self.listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    # root.iconbitmap("icon.ico")
    app = AutoClickerApp(root)
    root.mainloop()
