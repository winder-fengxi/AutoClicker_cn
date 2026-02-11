#include <windows.h>

// 全局状态控制变量
// Global state
volatile bool g_Running = false; // 控制点击循环是否继续的标志
HANDLE g_hThread = NULL;         // 指向后台点击线程的句柄

// 选项结构体，用于从 Python 接收参数
// Options Structure
struct ClickerOptions {
    int intervalMs;       // 点击间隔 (毫秒)
    int buttonCode;       // 鼠标按键代码: 0=左键, 1=右键, 2=中键
    int loopMode;         // 循环模式: 0=无限循环, 1=有限次数
    int loopCount;        // 循环次数: 当 loopMode=1 时有效
    int locationMode;     // 位置模式: 0=当前位置, 1=固定坐标
    int fixedX;           // 固定坐标 X (当 locationMode=1 时有效)
    int fixedY;           // 固定坐标 Y (当 locationMode=1 时有效)
    int doubleClick;      // 点击类型: 0=单击, 1=双击
};

// 点击循环线程函数
// Click loop function
DWORD WINAPI ClickLoop(LPVOID lpParam) {
    // 1. 提取参数
    // Extract parameters
    ClickerOptions* opts = (ClickerOptions*)lpParam;
    
    // 2. 将参数缓存到局部变量以提高访问速度
    // Cache local variables for speed
    int intervalMs = opts->intervalMs;
    int buttonCode = opts->buttonCode;
    int loopMode = opts->loopMode;
    long long loopCount = opts->loopCount; // 使用 long long 防止溢出
    int locationMode = opts->locationMode;
    int fixedX = opts->fixedX;
    int fixedY = opts->fixedY;
    bool isDoubleClick = (opts->doubleClick == 1);

    // 3. 参数已复制，立即释放结构体内存
    // Clean up parameter memory immediately
    delete opts;

    int downFlag = 0; // 鼠标按下标志
    int upFlag = 0;   // 鼠标抬起标志

    // 4. 根据按键代码映射 Win32 API 标志
    // Map button type to flags
    if (buttonCode == 0) { // 左键 Left
        downFlag = MOUSEEVENTF_LEFTDOWN;
        upFlag = MOUSEEVENTF_LEFTUP;
    } else if (buttonCode == 1) { // 右键 Right
        downFlag = MOUSEEVENTF_RIGHTDOWN;
        upFlag = MOUSEEVENTF_RIGHTUP;
    } else if (buttonCode == 2) { // 中键 Middle
        downFlag = MOUSEEVENTF_MIDDLEDOWN;
        upFlag = MOUSEEVENTF_MIDDLEUP;
    }

    long long currentCount = 0; // 当前已执行点击次数

    // 5. 进入点击主循环
    while (g_Running) {
        // [步骤 1] 移动鼠标 (如果是固定坐标模式)
        // Move Mouse if Fixed Location
        if (locationMode == 1) {
            SetCursorPos(fixedX, fixedY);
        }

        // [步骤 2] 执行点击动作 (按下 + 抬起)
        // Perform click
        if (downFlag != 0) mouse_event(downFlag, 0, 0, 0, 0);
        if (upFlag != 0) mouse_event(upFlag, 0, 0, 0, 0);

        // [步骤 3] 双击处理 (如果是双击模式，再点一次)
        // Double Click?
        if (isDoubleClick) {
            if (downFlag != 0) mouse_event(downFlag, 0, 0, 0, 0);
            if (upFlag != 0) mouse_event(upFlag, 0, 0, 0, 0);
        }

        // [步骤 4] 检查循环次数
        // Check Loop Count
        if (loopMode == 1) {
            currentCount++;
            if (currentCount >= loopCount) {
                g_Running = false; // 达到次数，停止运行
                break;
            }
        }

        // [步骤 5] 休眠等待下一次点击
        // Sleep
        Sleep(intervalMs);
    }
    
    return 0;
}

extern "C" {
    // 导出函数：启动连点器
    // Exported function to start clicking with full options
    __declspec(dllexport) void StartClicker(
        int intervalMs, 
        int buttonCode, 
        int loopMode, 
        int loopCount,
        int locationMode,
        int fixedX,
        int fixedY,
        int doubleClick
    ) {
        if (g_Running) return; // 防止重复启动

        g_Running = true;
        
        // 创建参数对象并在堆上分配内存 (传递给线程)
        // Pass parameters to thread
        ClickerOptions* opts = new ClickerOptions();
        opts->intervalMs = intervalMs;
        opts->buttonCode = buttonCode;
        opts->loopMode = loopMode;
        opts->loopCount = loopCount;
        opts->locationMode = locationMode;
        opts->fixedX = fixedX;
        opts->fixedY = fixedY;
        opts->doubleClick = doubleClick;

        // 创建 Windows 本地线程执行点击循环
        // Start Windows Thread
        g_hThread = CreateThread(
            NULL, 0, ClickLoop, opts, 0, NULL); 
    }

    // 导出函数：停止连点器
    // Exported function to stop clicking
    __declspec(dllexport) void StopClicker() {
        if (!g_Running) return;

        g_Running = false; // 设置标志位，通知线程退出循环
        
        // 等待线程安全结束
        if (g_hThread != NULL) {
            WaitForSingleObject(g_hThread, INFINITE);
            CloseHandle(g_hThread); // 关闭句柄释放资源
            g_hThread = NULL;
        }
    }
    
    // 导出函数：检查运行状态
    // Check is running
    __declspec(dllexport) bool IsRunning() {
        return g_Running;
    }
}
