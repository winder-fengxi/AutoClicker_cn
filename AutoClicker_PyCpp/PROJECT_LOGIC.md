# 项目运行逻辑说明 (Project Logic Documentation)

## 1. 项目架构概述 (Architecture Overview)

本项目采用 **Python + C++ 混合架构**，旨在结合 Python 快速开发 UI 的优势与 C++ 底层系统调用的高性能特性。

*   **前端 (Frontend)**: `app.py`
    *   使用 **Python (Tkinter)** 构建图形用户界面 (GUI)。
    *   负责处理用户输入（时间间隔、重复次数、坐标等）。
    *   负责热键监听 (`pynput`) 和鼠标坐标拾取。
    *   通过 `ctypes` 库调用 C++ 编写的动态链接库 (DLL)。

*   **后端 (Backend)**: `clicker_core.cpp` -> `clicker_core.dll`
    *   使用 **C++ (Win32 API)** 编写。
    *   负责核心的点击循环逻辑（高性能、低延迟）。
    *   在独立线程中运行，避免阻塞 UI 线程。
    *   直接调用 Windows API (`mouse_event`, `SetCursorPos`) 模拟鼠标操作。

---

## 2. 核心组件详解

### 2.1 C++ 核心 (`clicker_core.cpp`)

该文件被编译为 `clicker_core.dll`，提供了三个导出函数供 Python 调用：

1.  **`StartClicker(...)`**:
    *   接收来自 Python 的所有配置参数（间隔、按键类型、循环模式、坐标等）。
    *   将参数封装进 `ClickerOptions` 结构体。
    *   使用 `CreateThread` 创建一个新的 Windows 后台线程执行点击任务。
    *   设置全局标志 `g_Running = true`。

2.  **`StopClicker()`**:
    *   将全局标志 `g_Running` 设为 `false`，通知后台线程停止循环。
    *   使用 `WaitForSingleObject` 等待后台线程安全退出，防止资源泄露。

3.  **`ClickLoop(Thread Function)`**:
    *   实际执行点击的后台线程函数。
    *   解析传入的参数。
    *   进入 `while(g_Running)` 循环：
        1.  **移动鼠标** (如果选择了“指定坐标”模式)。
        2.  **执行点击** (使用 `mouse_event` 模拟按下和抬起)。
        3.  **双击处理** (如果选择了“双击”，则执行两次)。
        4.  **计数检查** (如果设定了有限次数，达到次数后自动退出)。
        5.  **休眠** (`Sleep(intervalMs)`) 等待下一次点击。

### 2.2 Python 界面 (`app.py`)

主程序入口，定义了 `AutoClickerApp` 类：

1.  **初始化 (`__init__`)**:
    *   加载语言文件 (`languages.json`)。
    *   构建 UI 界面 (`build_ui`)，包含各种输入框、单选按钮和下拉菜单。
    *   **加载 DLL (`load_dll`)**: 使用 `ctypes.CDLL` 加载 `clicker_core.dll`，并定义 C++ 函数的参数类型 (`argtypes`) 和返回值类型 (`restype`)，确保数据传输正确。
    *   **启动热键监听**: 使用 `pynput.keyboard.GlobalHotKeys` 在后台监听 F6 (开始/停止) 和 F8 (其他功能)。

2.  **用户交互**:
    *   **开始点击 (`start_clicking`)**: 
        *   从 UI 控件读取所有值（时/分/秒、重复次数、坐标）。
        *   将这些值转换为整数和枚举索引。
        *   调用 C++ 的 `self.clicker_lib.StartClicker(...)`。
    *   **选取坐标 (`start_pick_location`)**:
        *   启动 `pynput.mouse.Listener` 监听下一次鼠标点击。
        *   捕获点击坐标后，自动填入 X/Y 输入框并停止监听。

---

## 3. 数据流向 (Data Flow)

1.  **用户** 在 Tkinter 界面输入参数（例如：间隔 100ms，左键，重复 5 次）。
2.  **Python** 读取这些参数，转换为 C 语言兼容的整型数据 (C Integers)。
3.  **Python** 通过 `ctypes` 调用 DLL 函数 `StartClicker(100, 0, 1, 5, ...)`。
4.  **C++ DLL** 接收参数，开启新线程。
5.  **C++ 线程** 每隔 100ms 调用一次 Win32 API `mouse_event`。
6.  **用户** 按下 F6 或点击停止按钮。
7.  **Python** 调用 DLL 函数 `StopClicker()`。
8.  **C++ 线程** 检测到停止信号，退出循环，线程结束。

## 4. 编译与运行 (Build & Run)

项目的 `.vscode/tasks.json` 配置了自动编译流程：

1.  **编译任务**: 调用 MinGW 的 `g++` 编译器。
    *   命令: `g++ -shared -o clicker_core.dll clicker_core.cpp -static`
    *   作用: 将 C++ 源码编译为 Windows 动态链接库。
2.  **运行任务**: 启动 Python 解释器运行 `app.py`。
    *   Python 自动加载同目录下的 `clicker_core.dll`。

---
**注意**: 由于使用了 `Windows.h` 和 `ctypes` 加载 DLL，本项目仅能在 **Windows 操作系统** 上运行。
