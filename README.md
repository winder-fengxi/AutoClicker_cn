# AutoClicker

[![中文](https://img.shields.io/badge/语言-中文-blue)](README.md) [![English](https://img.shields.io/badge/Language-English-lightgrey)](README.en.md)

本项目复刻自[AutoClicker](https://github.com/oriash93/AutoClicker)  
本项目使用Python和C++编写，提供了一个自动点击器的功能，支持热键设置和多语言界面。（因为我不会C#）  
本项目使用了windows库，目前仅支持Windows系统，未来可能会添加对其他平台的支持。  
UI界面较为简陋，功能也较为基础，但我会持续更新和改进。欢迎大家提出建议和反馈！  

## 功能列表  

- 自动点击功能：可以设置点击的间隔时间和点击的坐标位置，支持左键、右键和中键点击。  
- 热键设置功能：可以设置开始和停止自动点击的热键，当前支持单键（如 F6/F7、字母、数字等）。  
- 多语言支持：界面支持多种语言，用户可以根据需要选择。  

## 使用说明  

下载最新的发布版本，解压后运行exe文件即可。  
下拉菜单中可以替换语言版本，如果需要其他语言，请联系我提供翻译文本。

## 从源码重建

### 1) 环境准备

- 操作系统：Windows 10/11
- Python：建议 3.10+
- C++ 编译器：MinGW-w64（需要 `g++`）

### 2) 克隆并进入项目

```powershell
git clone https://github.com/oriash93/AutoClicker.git
cd AutoClicker
```

### 3) 创建 Python 虚拟环境并安装依赖

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install pynput pyinstaller
```

### 4) 编译 C++ 核心 DLL

在 `AutoClicker_PyCpp` 目录执行：

```powershell
cd AutoClicker_PyCpp
g++ -shared -o clicker_core.dll clicker_core.cpp -static -lwinmm
cd ..
```

> 如果你在 VS Code 中，也可以直接运行任务：`Build C++ DLL (MinGW)`。

### 5) 直接运行

```powershell
python .\AutoClicker_PyCpp\app.py
```  

## 未来计划  

兼容更多平台
