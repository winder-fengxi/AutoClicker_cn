import tkinter as tk
from tkinter import ttk


def build_main_ui(app) -> None:
    """构建主窗口 UI。"""
    main_pad = 5

    top_frame = ttk.Frame(app.root)
    top_frame.pack(fill=tk.X)

    lang_frame = ttk.Frame(top_frame)
    lang_frame.pack(side=tk.RIGHT, padx=5)
    app.lbl_language = ttk.Label(lang_frame, text=app.lang["language_label"])
    app.lbl_language.pack(side=tk.LEFT)
    combo_lang = ttk.Combobox(lang_frame, values=["zh_cn", "en"], state="readonly", width=8)
    combo_lang.set(app.current_lang)
    combo_lang.pack(side=tk.LEFT)
    combo_lang.bind("<<ComboboxSelected>>", lambda e: app.change_language(combo_lang.get()))

    app.group_interval = ttk.LabelFrame(app.root, text=app.lang["click_interval"], padding=10)
    app.group_interval.pack(fill=tk.X, padx=main_pad, pady=5)

    int_frame = ttk.Frame(app.group_interval)
    int_frame.pack(fill=tk.X)

    def create_time_entry(parent, var, label_key):
        frame = ttk.Frame(parent)
        frame.pack(side=tk.LEFT, padx=5, expand=True)
        ttk.Entry(frame, textvariable=var, width=5).pack(side=tk.LEFT)
        label = ttk.Label(frame, text=app.lang[label_key])
        label.pack(side=tk.LEFT, padx=2)
        return label

    app.lbl_hours = create_time_entry(int_frame, app.hours_var, "hours")
    app.lbl_mins = create_time_entry(int_frame, app.mins_var, "mins")
    app.lbl_secs = create_time_entry(int_frame, app.secs_var, "secs")
    app.lbl_millis = create_time_entry(int_frame, app.millis_var, "millis")

    mid_frame = ttk.Frame(app.root)
    mid_frame.pack(fill=tk.X, padx=main_pad, pady=5)

    app.group_repeat = ttk.LabelFrame(mid_frame, text=app.lang["click_repeat"], padding=10)
    app.group_repeat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

    app.rb_repeat_inf = ttk.Radiobutton(
        app.group_repeat,
        text=app.lang["repeat_until_stopped"],
        variable=app.repeat_mode_var,
        value="Infinite",
    )
    app.rb_repeat_inf.pack(anchor=tk.W, pady=2)

    repeat_cnt_frame = ttk.Frame(app.group_repeat)
    repeat_cnt_frame.pack(anchor=tk.W, pady=2)
    app.rb_repeat_count = ttk.Radiobutton(repeat_cnt_frame, text="", variable=app.repeat_mode_var, value="Count")
    app.rb_repeat_count.pack(side=tk.LEFT)
    ttk.Entry(repeat_cnt_frame, textvariable=app.repeat_count_var, width=6).pack(side=tk.LEFT, padx=5)
    app.lbl_times = ttk.Label(repeat_cnt_frame, text=app.lang["times"])
    app.lbl_times.pack(side=tk.LEFT)

    app.group_pos = ttk.LabelFrame(mid_frame, text=app.lang["cursor_position"], padding=10)
    app.group_pos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

    app.rb_pos_current = ttk.Radiobutton(
        app.group_pos,
        text=app.lang["current_location"],
        variable=app.location_mode_var,
        value="Current",
    )
    app.rb_pos_current.pack(anchor=tk.W, pady=2)

    pos_pick_frame = ttk.Frame(app.group_pos)
    pos_pick_frame.pack(anchor=tk.W, pady=2)
    app.rb_pos_picked = ttk.Radiobutton(pos_pick_frame, text="", variable=app.location_mode_var, value="Picked")
    app.rb_pos_picked.pack(side=tk.LEFT)

    ttk.Label(pos_pick_frame, text="X").pack(side=tk.LEFT, padx=2)
    ttk.Entry(pos_pick_frame, textvariable=app.picked_x_var, width=4).pack(side=tk.LEFT)
    ttk.Label(pos_pick_frame, text="Y").pack(side=tk.LEFT, padx=2)
    ttk.Entry(pos_pick_frame, textvariable=app.picked_y_var, width=4).pack(side=tk.LEFT)

    app.btn_pick = ttk.Button(pos_pick_frame, text="🎯", width=3, command=app.start_pick_location)
    app.btn_pick.pack(side=tk.LEFT, padx=5)

    app.group_mouse = ttk.LabelFrame(app.root, text=app.lang["mouse_options"], padding=10)
    app.group_mouse.pack(fill=tk.X, padx=main_pad, pady=5)

    opts_frame = ttk.Frame(app.group_mouse)
    opts_frame.pack(fill=tk.X)

    app.lbl_mouse_btn = ttk.Label(opts_frame, text=app.lang["mouse_button"])
    app.lbl_mouse_btn.pack(side=tk.LEFT, padx=(0, 5))

    app.combo_btn = ttk.Combobox(opts_frame, state="readonly", width=10)
    app.combo_btn["values"] = [app.lang["left"], app.lang["right"], app.lang["middle"]]
    app.combo_btn.current({"Left": 0, "Right": 1, "Middle": 2}.get(app.button_var.get(), 0))
    app.combo_btn.pack(side=tk.LEFT, padx=(0, 20))
    app.combo_btn.bind("<<ComboboxSelected>>", app.on_combo_change)

    app.lbl_click_type = ttk.Label(opts_frame, text=app.lang["click_type"])
    app.lbl_click_type.pack(side=tk.LEFT, padx=(0, 5))

    app.combo_type = ttk.Combobox(opts_frame, state="readonly", width=10)
    app.combo_type["values"] = [app.lang["single"], app.lang["double"]]
    app.combo_type.current({"Single": 0, "Double": 1}.get(app.click_type_var.get(), 0))
    app.combo_type.pack(side=tk.LEFT)
    app.combo_type.bind("<<ComboboxSelected>>", app.on_combo_change)

    btn_frame = ttk.Frame(app.root)
    btn_frame.pack(fill=tk.X, padx=main_pad, pady=10)

    b_row1 = ttk.Frame(btn_frame)
    b_row1.pack(fill=tk.X, pady=2)

    app.btn_start = ttk.Button(b_row1, text=app.get_start_button_text(), command=app.start_clicking)
    app.btn_start.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

    app.btn_stop = ttk.Button(b_row1, text=app.get_stop_button_text(), command=app.stop_clicking)
    app.btn_stop.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

    b_row2 = ttk.Frame(btn_frame)
    b_row2.pack(fill=tk.X, pady=5)

    app.btn_save = ttk.Button(b_row2, text=app.lang["save_settings"], command=app.save_settings)
    app.btn_save.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

    app.btn_hotkeys = ttk.Button(b_row2, text=app.lang["hotkeys"], command=app.open_hotkey_settings)
    app.btn_hotkeys.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

    app.chk_top = ttk.Checkbutton(
        b_row2,
        text=app.lang["top_most"],
        variable=app.chk_top_var,
        command=app.toggle_top_window,
    )
    app.chk_top.pack(side=tk.RIGHT, padx=5)

    app.lbl_status = tk.Label(app.root, textvariable=app.status_var, font=("Arial", 10, "bold"), fg="red")
    app.lbl_status.pack(pady=5)

    app.toggle_top_window()

    if not app.clicker_service.available:
        ttk.Label(app.root, text=app.lang.get("error_dll", ""), foreground="red").pack()
