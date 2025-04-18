# Task Tracker 🚀

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Tkinter](https://img.shields.io/badge/Tkinter-%233776AB.svg?style=for-the-badge&logo=python&logoColor=white)
![ttkbootstrap](https://img.shields.io/badge/ttkbootstrap-3.0.0-blue?style=for-the-badge)

A modern desktop application for task management with priority scheduling and reminders.

## ✨ Features

- 📝 Create, edit, and delete tasks
- ⏰ Set deadlines and reminders
- 🎨 Modern UI with ttkbootstrap themes
- 🔍 Search and filter tasks
- 📊 Priority-based scheduling
- 💾 JSON data persistence
- 🔄 Undo/Redo functionality

## 📦 Dependencies

```python
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
import threading
import json
from datetime import datetime, timedelta
import os
import heapq
from collections import deque

