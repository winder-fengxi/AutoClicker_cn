# AutoClicker

[![中文](https://img.shields.io/badge/语言-中文-lightgrey)](README.md) [![English](https://img.shields.io/badge/Language-English-blue)](README.en.md)

This project is a remake of [AutoClicker](https://github.com/oriash93/AutoClicker).  
It is written in Python and C++, and provides auto-clicking, hotkey configuration, and multilingual UI support.  
It currently relies on Windows APIs, so it is Windows-only for now (cross-platform support may be added in the future).  
The UI is simple and the feature set is basic, but the project will continue to improve. Feedback is welcome.

## Features

- Auto click: configurable click interval and click position, with left/right/middle mouse button support.
- Hotkey settings: configurable start/stop hotkeys, currently single-key only (for example F6/F7, letters, numbers).
- Multi-language UI: language can be switched from the app.

## Usage

Download the latest release, extract it, and run the executable.  
You can switch UI language from the dropdown menu. If you need another language, feel free to contact me with translation text.

## Rebuild from Source

### 1) Prerequisites

- OS: Windows 10/11
- Python: recommended 3.10+
- C++ compiler: MinGW-w64 (with `g++`)

### 2) Clone and enter the repo

```powershell
git clone https://github.com/oriash93/AutoClicker.git
cd AutoClicker
```

### 3) Create virtual environment and install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install pynput pyinstaller
```

### 4) Build the C++ core DLL

Run in the `AutoClicker_PyCpp` directory:

```powershell
cd AutoClicker_PyCpp
g++ -shared -o clicker_core.dll clicker_core.cpp -static -lwinmm
cd ..
```

> In VS Code, you can also run the task: `Build C++ DLL (MinGW)`.

### 5) Run directly (development)

```powershell
python .\AutoClicker_PyCpp\app.py
```

## Roadmap

- Better cross-platform support
