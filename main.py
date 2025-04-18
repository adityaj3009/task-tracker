import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
import threading
import json
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import os
import heapq
from collections import deque

class Task:
    """Node class for task linked list implementation"""
    def __init__(self, content, priority=0, deadline=None, tags=None, subtasks=None):
        self.content = content
        self.priority = priority  
        self.deadline = deadline
        self.completion_time = None
        self.tags = tags or []
        self.subtasks = subtasks or []
        self.next = None
        self.prev = None
        self.creation_time = datetime.now()
        self.reminder_time = None

    def __lt__(self, other):
        
        if self.priority != other.priority:
            return self.priority < other.priority
        if self.deadline and other.deadline:
            return self.deadline < other.deadline
        if self.deadline:
            return True
        return False
        
    def to_dict(self):
        """Convert task to dictionary for JSON serialization"""
        return {
            "content": self.content,
            "priority": self.priority,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "completion_time": self.completion_time.isoformat() if self.completion_time else None,
            "tags": self.tags,
            "subtasks": self.subtasks,
            "creation_time": self.creation_time.isoformat(),
            "reminder_time": self.reminder_time.isoformat() if self.reminder_time else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a Task from dictionary data"""
        task = cls(
            content=data["content"],
            priority=data["priority"],
            deadline=datetime.fromisoformat(data["deadline"]) if data["deadline"] else None,
            tags=data["tags"],
            subtasks=data["subtasks"]
        )
        task.creation_time = datetime.fromisoformat(data["creation_time"])
        if data["completion_time"]:
            task.completion_time = datetime.fromisoformat(data["completion_time"])
        if data["reminder_time"]:
            task.reminder_time = datetime.fromisoformat(data["reminder_time"])
        return task


class TaskLinkedList:
    """Doubly linked list implementation for tasks"""
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0
        
    def append(self, task):
        """Add a task to the end of the list"""
        if not self.head:
            self.head = task
            self.tail = task
        else:
            task.prev = self.tail
            self.tail.next = task
            self.tail = task
        self.size += 1
        
    def pop(self, task):
        """Remove a specific task from the list"""
        if not task:
            return None
            
        if task == self.head and task == self.tail:
            self.head = None
            self.tail = None
        elif task == self.head:
            self.head = task.next
            if self.head:
                self.head.prev = None
        elif task == self.tail:
            self.tail = task.prev
            if self.tail:
                self.tail.next = None
        else:
            task.prev.next = task.next
            task.next.prev = task.prev
            
        self.size -= 1
        return task
        
    def get_all_tasks(self):
        """Return all tasks as a list"""
        tasks = []
        current = self.head
        while current:
            tasks.append(current)
            current = current.next
        return tasks
        
    def binary_search(self, target_content):
        """Search for a task by content using binary search (after sorting)"""
        tasks = sorted(self.get_all_tasks(), key=lambda x: x.content)
        
        left, right = 0, len(tasks) - 1
        while left <= right:
            mid = (left + right) // 2
            if tasks[mid].content == target_content:
                return tasks[mid]
            elif tasks[mid].content < target_content:
                left = mid + 1
            else:
                right = mid - 1
                
        return None
        
    def merge_sort(self, key_func=None):
        """Sort tasks using merge sort and return sorted list"""
        tasks = self.get_all_tasks()
        if not key_func:
            key_func = lambda x: x.content
            
        if len(tasks) <= 1:
            return tasks
            
        def merge_sort_internal(arr):
            if len(arr) <= 1:
                return arr
                
            mid = len(arr) // 2
            left = merge_sort_internal(arr[:mid])
            right = merge_sort_internal(arr[mid:])
            
            return merge(left, right)
            
        def merge(left, right):
            result = []
            i = j = 0
            
            while i < len(left) and j < len(right):
                if key_func(left[i]) <= key_func(right[j]):
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1
                    
            result.extend(left[i:])
            result.extend(right[j:])
            return result
            
        return merge_sort_internal(tasks)


class TaskTree:
    """Implementation of a tree structure for categorized tasks"""
    class TreeNode:
        def __init__(self, name):
            self.name = name
            self.tasks = []
            self.children = []
            
        def add_child(self, child):
            self.children.append(child)
            return child
            
        def add_task(self, task):
            self.tasks.append(task)
            
    def __init__(self):
        self.root = self.TreeNode("Root")
        
    def add_category(self, path, create_missing=True):
        """Add a category at the specified path (e.g., 'Work/Project A')"""
        if not path:
            return self.root
            
        parts = path.split('/')
        current = self.root
        
        for part in parts:
            found = False
            for child in current.children:
                if child.name == part:
                    current = child
                    found = True
                    break
                    
            if not found:
                if create_missing:
                    new_node = self.TreeNode(part)
                    current.add_child(new_node)
                    current = new_node
                else:
                    return None
                    
        return current
        
    def add_task_to_category(self, path, task):
        """Add a task to a specific category"""
        node = self.add_category(path)
        if node:
            node.add_task(task)
            
    def dfs_traverse(self):
        """Depth-first traversal of the tree"""
        result = []
        
        def dfs(node, path=""):
            current_path = f"{path}/{node.name}" if path else node.name
            for task in node.tasks:
                result.append((current_path, task))
            for child in node.children:
                dfs(child, current_path)
                
        dfs(self.root)
        return result


class ModernTodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Team J")
        
        
        window_width = 900
        window_height = 700
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        position_x = int((screen_width / 2) - (window_width / 2))
        position_y = int((screen_height / 2) - (window_height / 2))
        self.root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
        
        
        self.style = ttk.Style(theme="superhero")
        
        
        self.task_list = TaskLinkedList()          
        self.completed_tasks = TaskLinkedList()    
        self.task_tree = TaskTree()                
        self.priority_queue = []                   
        self.history_stack = []                    
        self.future_stack = []                     
        self.task_queue = deque()                  
        
        
        self.heading_text = tk.StringVar(value="Team J")
        self.selected_font = tk.StringVar(value="Roboto")
        self.current_category = tk.StringVar(value="All Tasks")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search_change)
        self.task_var = tk.StringVar()
        self.filter_mode = tk.StringVar(value="All")
        self.view_mode = tk.StringVar(value="List")
        self.dark_mode = tk.BooleanVar(value=False)
        
        
        self.selected_task = None
        self.last_action = None
        self.reminder_threads = {}
        
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        
        self.sidebar = ttk.Frame(self.main_container, bootstyle=SECONDARY)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        
        
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        
        self.setup_header()
        
        
        self.setup_sidebar()
        
        
        self.setup_content()
        
        
        self.setup_footer()
        
    def setup_header(self):
        
        header = ttk.Frame(self.content_frame, bootstyle=PRIMARY)
        header.pack(fill=tk.X, pady=0)
        
        
        title_frame = ttk.Frame(header)
        title_frame.pack(fill=tk.X, padx=15, pady=10)
        
        
        title_label = ttk.Label(
            title_frame, 
            textvariable=self.heading_text, 
            font=("Roboto", 20, "bold"),
            bootstyle="inverse"
        )
        title_label.pack(side=tk.LEFT)
        title_label.bind("<Button-1>", self.change_heading)
        
        
        search_frame = ttk.Frame(title_frame)
        search_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(50, 0))
        
        search_icon = ttk.Label(search_frame, text="🔍", font=("Segoe UI Emoji", 12))
        search_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        search_entry = ttk.Entry(
            search_frame, 
            textvariable=self.search_var,
            font=("Roboto", 11),
            bootstyle="dark",
            width=25
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        
        btn_frame = ttk.Frame(header)
        btn_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        view_btn = ttk.Menubutton(
            btn_frame, 
            text="View", 
            bootstyle=OUTLINE
        )
        view_btn.pack(side=tk.LEFT, padx=5)
        
        view_menu = tk.Menu(view_btn, tearoff=0)
        view_menu.add_radiobutton(label="List View", variable=self.view_mode, value="List", command=self.update_view)
        view_menu.add_radiobutton(label="Kanban View", variable=self.view_mode, value="Kanban", command=self.update_view)
        view_menu.add_radiobutton(label="Calendar View", variable=self.view_mode, value="Calendar", command=self.update_view)
        view_btn["menu"] = view_menu
        
        filter_btn = ttk.Menubutton(
            btn_frame, 
            text="Filter", 
            bootstyle=OUTLINE
        )
        filter_btn.pack(side=tk.LEFT, padx=5)
        
        filter_menu = tk.Menu(filter_btn, tearoff=0)
        filter_menu.add_radiobutton(label="All Tasks", variable=self.filter_mode, value="All", command=self.update_view)
        filter_menu.add_radiobutton(label="Due Today", variable=self.filter_mode, value="Today", command=self.update_view)
        filter_menu.add_radiobutton(label="High Priority", variable=self.filter_mode, value="Priority", command=self.update_view)
        filter_menu.add_radiobutton(label="Completed", variable=self.filter_mode, value="Completed", command=self.update_view)
        filter_btn["menu"] = filter_menu
        
        sort_btn = ttk.Menubutton(
            btn_frame, 
            text="Sort", 
            bootstyle=OUTLINE
        )
        sort_btn.pack(side=tk.LEFT, padx=5)
        
        sort_menu = tk.Menu(sort_btn, tearoff=0)
        sort_menu.add_command(label="By Priority", command=lambda: self.sort_tasks("priority"))
        sort_menu.add_command(label="By Due Date", command=lambda: self.sort_tasks("deadline"))
        sort_menu.add_command(label="By Creation Time", command=lambda: self.sort_tasks("creation_time"))
        sort_menu.add_command(label="Alphabetically", command=lambda: self.sort_tasks("content"))
        sort_btn["menu"] = sort_menu
        
        
        ttk.Button(
            btn_frame, 
            text="Import",
            bootstyle=SECONDARY,
            command=self.import_data
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Export",
            bootstyle=SECONDARY,
            command=self.export_data
        ).pack(side=tk.RIGHT, padx=5)
        
        dark_mode_toggle = ttk.Checkbutton(
            btn_frame,
            text="Dark Mode",
            variable=self.dark_mode,
            bootstyle="round-toggle",
            command=self.toggle_dark_mode
        )
        dark_mode_toggle.pack(side=tk.RIGHT, padx=15)
    
    def setup_sidebar(self):
        
        sidebar_header = ttk.Frame(self.sidebar, bootstyle=PRIMARY)
        sidebar_header.pack(fill=tk.X, pady=0)
        
        ttk.Label(
            sidebar_header, 
            text="Categories", 
            font=("Roboto", 14, "bold"),
            bootstyle="inverse",
            anchor=tk.CENTER
        ).pack(fill=tk.X, padx=10, pady=10)
        
        
        ttk.Button(
            sidebar_header,
            text="+ Add Category",
            bootstyle=SECONDARY,
            command=self.add_category
        ).pack(fill=tk.X, padx=10, pady=(0, 10))
        
        
        category_frame = ScrolledFrame(self.sidebar, autohide=True)
        category_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        
        self.category_buttons = []
        
        
        all_btn = ttk.Button(
            category_frame,
            text="All Tasks",
            bootstyle=SUCCESS,
            command=lambda: self.change_category("All Tasks")
        )
        all_btn.pack(fill=tk.X, padx=5, pady=2)
        self.category_buttons.append(all_btn)
        
        
        categories = ["Work", "Personal", "Shopping", "Health", "Education"]
        for category in categories:
            self.task_tree.add_category(category)
            btn = ttk.Button(
                category_frame,
                text=category,
                bootstyle=SECONDARY,
                command=lambda c=category: self.change_category(c)
            )
            btn.pack(fill=tk.X, padx=5, pady=2)
            self.category_buttons.append(btn)
    
    def setup_content(self):
        
        input_frame = ttk.Frame(self.content_frame, bootstyle=PRIMARY)
        input_frame.pack(fill=tk.X, padx=15, pady=10)
        
        
        self.task_entry = ttk.Entry(
            input_frame,
            textvariable=self.task_var,
            font=("Roboto", 12),
            bootstyle="dark",
            width=40
        )
        self.task_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.task_entry.bind("<Return>", self.add_task)
        
        self.task_var.set("Add a new task...")
        self.task_entry.bind("<FocusIn>", self.on_entry_focus_in)
        self.task_entry.bind("<FocusOut>", self.on_entry_focus_out)
        
        
        ttk.Button(
            input_frame,
            text="Add Task",
            bootstyle=SUCCESS,
            command=self.add_task
        ).pack(side=tk.LEFT)
        
        
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        
        self.list_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.list_frame, text="Tasks")
        
        
        self.task_container = ScrolledFrame(self.list_frame, autohide=True)
        self.task_container.pack(fill=tk.BOTH, expand=True)
        
        
        self.completed_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.completed_frame, text="Completed")
        
        
        self.completed_container = ScrolledFrame(self.completed_frame, autohide=True)
        self.completed_container.pack(fill=tk.BOTH, expand=True)
        
        
        self.analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_frame, text="Analytics")
        
        ttk.Label(
            self.analytics_frame,
            text="Task Analytics Dashboard",
            font=("Roboto", 16, "bold")
        ).pack(pady=20)
        
        analytics_content = ttk.Frame(self.analytics_frame)
        analytics_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        
        metrics_frame = ttk.Frame(analytics_content)
        metrics_frame.pack(fill=tk.X, padx=10, pady=10)
        
        
        self.create_metric_card(metrics_frame, "Total Tasks", "0", 0)
        self.create_metric_card(metrics_frame, "Completed", "0", 1)
        self.create_metric_card(metrics_frame, "Completion Rate", "0%", 2)
        self.create_metric_card(metrics_frame, "Overdue", "0", 3)
        
        
        canvas_frame = ttk.Frame(analytics_content, bootstyle=SECONDARY)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(
            canvas_frame,
            text="Task Completion Trends",
            font=("Roboto", 14, "bold"),
            anchor=tk.CENTER
        ).pack(pady=10)
        
        
        chart_placeholder = ttk.Frame(canvas_frame, height=250)
        chart_placeholder.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(
            chart_placeholder,
            text="[Productivity trends visualization would appear here]",
            font=("Roboto", 12),
            anchor=tk.CENTER
        ).pack(expand=True)
        
    def setup_footer(self):
        footer = ttk.Frame(self.content_frame, bootstyle=SECONDARY)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        
        
        status_label = ttk.Label(
            footer,
            text="Ready",
            bootstyle="inverse"
        )
        status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        
        ttk.Label(
            footer,
            text="v2.0.0",
            bootstyle="inverse"
        ).pack(side=tk.RIGHT, padx=10, pady=5)
        
    def create_metric_card(self, parent, title, value, column):
        card = ttk.Frame(parent, bootstyle=LIGHT)
        card.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")
        
        ttk.Label(
            card,
            text=title,
            font=("Roboto", 12),
            bootstyle=SECONDARY
        ).pack(pady=(10, 5))
        
        ttk.Label(
            card,
            text=value,
            font=("Roboto", 18, "bold")
        ).pack(pady=(0, 10))
        
        parent.columnconfigure(column, weight=1)
        
    def render_tasks(self):
        
        for widget in self.task_container.winfo_children():
            widget.destroy()
            
        
        tasks = self.get_filtered_tasks()
        
        
        total_tasks = self.task_list.size + self.completed_tasks.size
        completed_count = self.completed_tasks.size
        completion_rate = f"{(completed_count / total_tasks * 100) if total_tasks else 0:.1f}%"
        overdue_count = sum(1 for task in self.task_list.get_all_tasks() 
                           if task.deadline and task.deadline < datetime.now())
                           
        
        for widget in self.analytics_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                metrics_frame = widget.winfo_children()[0]
                for i, (title, value) in enumerate([
                    ("Total Tasks", str(total_tasks)),
                    ("Completed", str(completed_count)),
                    ("Completion Rate", completion_rate),
                    ("Overdue", str(overdue_count))
                ]):
                    card = metrics_frame.grid_slaves(row=0, column=i)[0]
                    value_label = card.winfo_children()[1]
                    value_label.configure(text=value)
        
        
        if not tasks:
            empty_label = ttk.Label(
                self.task_container,
                text="No tasks found. Create a new task to get started!",
                font=("Roboto", 12),
                bootstyle=SECONDARY
            )
            empty_label.pack(pady=50)
            return
            
        
        for task in tasks:
            self.create_task_card(self.task_container, task)
            
        
        
        for widget in self.completed_container.winfo_children():
            widget.destroy()
            
        completed_tasks = self.completed_tasks.get_all_tasks()
        if not completed_tasks:
            empty_label = ttk.Label(
                self.completed_container,
                text="No completed tasks yet. Complete a task to see it here!",
                font=("Roboto", 12),
                bootstyle=SECONDARY
            )
            empty_label.pack(pady=50)
        else:
            for task in completed_tasks:
                self.create_completed_card(self.completed_container, task)
                
    def create_task_card(self, parent, task):
        
        card = ttk.Frame(parent, bootstyle=LIGHT)
        card.pack(fill=tk.X, padx=10, pady=5)
        
        
        priority_colors = {0: "success", 1: "warning", 2: "danger"}
        priority_color = priority_colors.get(task.priority, "secondary")
        
        
        content_frame = ttk.Frame(card)
        content_frame.pack(fill=tk.X, padx=10, pady=5)
        
        priority_indicator = ttk.Label(
            content_frame,
            text="●",
            font=("Segoe UI Symbol", 16),
            bootstyle=priority_color
        )
        priority_indicator.pack(side=tk.LEFT, padx=(0, 5))
        
        content_label = ttk.Label(
            content_frame,
            text=task.content,
            font=("Roboto", 12),
            wraplength=400,
            justify=tk.LEFT
        )
        content_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        
        menu_btn = ttk.Button(
            content_frame,
            text="⋮",
            bootstyle=SECONDARY,
            width=3
        )
        menu_btn.pack(side=tk.RIGHT, padx=5)
        
        
        menu = tk.Menu(menu_btn, tearoff=0)
        menu.add_command(label="Edit Task", command=lambda: self.edit_task(task))
        menu.add_command(label="Set Reminder", command=lambda: self.set_reminder(task))
        menu.add_command(label="Change Priority", command=lambda: self.change_priority(task))
        menu.add_command(label="Add Subtask", command=lambda: self.add_subtask(task))
        menu.add_command(label="Move to Category", command=lambda: self.move_to_category(task))
        menu.add_separator()
        menu.add_command(label="Complete Task", command=lambda: self.complete_task(task))
        menu.add_command(label="Delete Task", command=lambda: self.delete_task(task))
        
        menu_btn.configure(command=lambda: menu.tk_popup(
            menu_btn.winfo_rootx(),
            menu_btn.winfo_rooty() + menu_btn.winfo_height()
        ))
        
        
        footer_frame = ttk.Frame(card)
        footer_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        
        if task.deadline:
            deadline_str = task.deadline.strftime("%b %d, %Y")
            deadline_label = ttk.Label(
                footer_frame,
                text=f"Due: {deadline_str}",
                font=("Roboto", 10),
                bootstyle=SECONDARY
            )
            deadline_label.pack(side=tk.LEFT, padx=(0, 10))
            
            
            if task.deadline < datetime.now():
                overdue_label = ttk.Label(
                    footer_frame,
                    text="⚠️ Overdue",
                    font=("Roboto", 10),
                    bootstyle="danger"
                )
                overdue_label.pack(side=tk.LEFT)
        
        
        if task.tags:
            tag_frame = ttk.Frame(footer_frame)
            tag_frame.pack(side=tk.RIGHT)
            
            for tag in task.tags[:2]:  
                tag_label = ttk.Label(
                    tag_frame,
                    text=tag,
                    font=("Roboto", 9),
                    bootstyle=f"{priority_color}-inverse",
                    padding=(5, 0)
                )
                tag_label.pack(side=tk.RIGHT, padx=2)
                
        
        for widget in [card, content_frame, content_label, footer_frame]:
            widget.bind("<Button-1>", lambda e, t=task: self.select_task(t))
            
        
        return card
        
    def create_completed_card(self, parent, task):
        
        card = ttk.Frame(parent, bootstyle=LIGHT)
        card.pack(fill=tk.X, padx=10, pady=5)
        
        
        content_frame = ttk.Frame(card)
        content_frame.pack(fill=tk.X, padx=10, pady=5)
        
        checkmark = ttk.Label(
            content_frame,
            text="✓",
            font=("Segoe UI Symbol", 14),
            bootstyle=SUCCESS
        )
        checkmark.pack(side=tk.LEFT, padx=(0, 5))
        
        content_label = ttk.Label(
            content_frame,
            text=task.content,
            font=("Roboto", 12, "overstrike"),  
            wraplength=400,
            justify=tk.LEFT,
            bootstyle=SECONDARY  
        )
        content_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        
        completion_time = task.completion_time.strftime("%b %d, %Y %H:%M")
        ttk.Label(
            content_frame,
            text=f"Completed: {completion_time}",
                        font=("Roboto", 9),
            bootstyle=SECONDARY
        ).pack(side=tk.RIGHT, padx=5)
        
        
        for widget in [card, content_frame, content_label]:
            widget.bind("<Button-1>", lambda e, t=task: self.select_task(t))
            
        return card

    def get_filtered_tasks(self):
        """Return tasks based on current filters and category"""
        if self.current_category.get() == "All Tasks":
            tasks = self.task_list.get_all_tasks()
        else:
            
            tasks = []
            for path, task in self.task_tree.dfs_traverse():
                if self.current_category.get() in path:
                    tasks.append(task)
        
        
        filter_mode = self.filter_mode.get()
        if filter_mode == "All":
            return tasks
        elif filter_mode == "Today":
            today = datetime.now().date()
            return [t for t in tasks if t.deadline and t.deadline.date() == today]
        elif filter_mode == "Priority":
            return [t for t in tasks if t.priority == 0]  
        elif filter_mode == "Completed":
            return self.completed_tasks.get_all_tasks()
        return tasks
        
    def select_task(self, task):
        """Select a task for detailed view or editing"""
        self.selected_task = task
        
        
    def add_task(self, event=None):
        """Add a new task to the list"""
        content = self.task_var.get().strip()
        if not content or content == "Add a new task...":
            return
            
        
        new_task = Task(content)
        
        
        self.task_list.append(new_task)
        if self.current_category.get() != "All Tasks":
            self.task_tree.add_task_to_category(self.current_category.get(), new_task)
            
        
        self.history_stack.append(("add", new_task))
        self.future_stack.clear()
        
        
        self.task_var.set("")
        self.render_tasks()
        
    def edit_task(self, task):
        """Edit an existing task"""
        new_content = simpledialog.askstring(
            "Edit Task",
            "Edit task content:",
            initialvalue=task.content,
            parent=self.root
        )
        if new_content and new_content != task.content:
            
            old_content = task.content
            self.history_stack.append(("edit", task, old_content))
            self.future_stack.clear()
            
            
            task.content = new_content
            self.render_tasks()
            
    def complete_task(self, task):
        """Mark a task as completed"""
        
        self.task_list.pop(task)
        
        
        task.completion_time = datetime.now()
        
        
        self.completed_tasks.append(task)
        
        
        self.history_stack.append(("complete", task))
        self.future_stack.clear()
        
        
        self.render_tasks()
        
    def delete_task(self, task):
        """Delete a task completely"""
        
        self.task_list.pop(task)
        
        
        self.history_stack.append(("delete", task))
        self.future_stack.clear()
        
        
        self.render_tasks()
        
    def undo(self):
        """Undo the last action"""
        if not self.history_stack:
            return
            
        action = self.history_stack.pop()
        self.future_stack.append(action)
        
        if action[0] == "add":
            
            task = action[1]
            self.task_list.pop(task)
        elif action[0] == "delete":
            
            task = action[1]
            self.task_list.append(task)
        elif action[0] == "edit":
            
            task, old_content = action[1], action[2]
            task.content = old_content
        elif action[0] == "complete":
            
            task = action[1]
            self.completed_tasks.pop(task)
            task.completion_time = None
            self.task_list.append(task)
            
        self.render_tasks()
        
    def redo(self):
        """Redo the last undone action"""
        if not self.future_stack:
            return
            
        action = self.future_stack.pop()
        self.history_stack.append(action)
        
        if action[0] == "add":
            
            task = action[1]
            self.task_list.append(task)
        elif action[0] == "delete":
            
            task = action[1]
            self.task_list.pop(task)
        elif action[0] == "edit":
            
            task, old_content = action[1], action[2]
            task.content = old_content
        elif action[0] == "complete":
            
            task = action[1]
            self.task_list.pop(task)
            task.completion_time = datetime.now()
            self.completed_tasks.append(task)
            
        self.render_tasks()
        
    def change_priority(self, task):
        """Change task priority"""
        new_priority = simpledialog.askinteger(
            "Change Priority",
            "Enter new priority (0=High, 1=Medium, 2=Low):",
            initialvalue=task.priority,
            minvalue=0,
            maxvalue=2,
            parent=self.root
        )
        if new_priority is not None and new_priority != task.priority:
            
            self.history_stack.append(("priority", task, task.priority))
            self.future_stack.clear()
            
            
            task.priority = new_priority
            self.render_tasks()
            
    def set_reminder(self, task):
        """Set a reminder for a task"""
        reminder_time = simpledialog.askstring(
            "Set Reminder",
            "Enter reminder time (e.g., 'in 1 hour' or 'tomorrow 9am'):",
            parent=self.root
        )
        if reminder_time:
            
            try:
                if reminder_time.startswith("in "):
                    parts = reminder_time[3:].split()
                    if parts[1].startswith("hour"):
                        delta = timedelta(hours=int(parts[0]))
                    elif parts[1].startswith("minute"):
                        delta = timedelta(minutes=int(parts[0]))
                    else:
                        delta = timedelta(days=int(parts[0]))
                else:
                    delta = timedelta(days=1)  
                    
                task.reminder_time = datetime.now() + delta
                
                
                self.start_reminder_thread(task)
                
                messagebox.showinfo("Reminder Set", f"Reminder set for {task.reminder_time}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not parse reminder time: {e}")
                
    def start_reminder_thread(self, task):
        """Start a thread to monitor reminder time"""
        if task in self.reminder_threads:
            self.reminder_threads[task].cancel()
            
        def check_reminder():
            while datetime.now() < task.reminder_time:
                time.sleep(1)
                
            
            if task in self.task_list.get_all_tasks():  
                messagebox.showwarning("Reminder", f"Don't forget: {task.content}")
                
        thread = threading.Thread(target=check_reminder)
        thread.daemon = True
        thread.start()
        self.reminder_threads[task] = thread
        
    def add_subtask(self, parent_task):
        """Add a subtask to a parent task"""
        subtask_content = simpledialog.askstring(
            "Add Subtask",
            "Enter subtask content:",
            parent=self.root
        )
        if subtask_content:
            parent_task.subtasks.append(subtask_content)
            self.render_tasks()
            
    def move_to_category(self, task):
        """Move task to a different category"""
        categories = ["Work", "Personal", "Shopping", "Health", "Education"]
        category = simpledialog.askstring(
            "Move to Category",
            "Enter category name:",
            initialvalue=self.current_category.get(),
            parent=self.root
        )
        if category and category != self.current_category.get():
            
            
            
            
            self.task_tree.add_task_to_category(category, task)
            self.render_tasks()
            
    def change_category(self, category_name):
        """Change the current category view"""
        self.current_category.set(category_name)
        self.render_tasks()
        
    def add_category(self):
        """Add a new custom category"""
        category_name = simpledialog.askstring(
            "Add Category",
            "Enter category name:",
            parent=self.root
        )
        if category_name:
            self.task_tree.add_category(category_name)
            
            
            btn = ttk.Button(
                self.sidebar.winfo_children()[2],  
                text=category_name,
                bootstyle=SECONDARY,
                command=lambda c=category_name: self.change_category(c)
            )
            btn.pack(fill=tk.X, padx=5, pady=2)
            self.category_buttons.append(btn)
            
    def sort_tasks(self, key):
        """Sort tasks by the specified key"""
        if key == "priority":
            key_func = lambda x: x.priority
        elif key == "deadline":
            key_func = lambda x: x.deadline or datetime.max
        elif key == "creation_time":
            key_func = lambda x: x.creation_time
        else:  
            key_func = lambda x: x.content.lower()
            
        sorted_tasks = self.task_list.merge_sort(key_func)
        
        
        self.task_list = TaskLinkedList()
        for task in sorted_tasks:
            self.task_list.append(task)
            
        self.render_tasks()
        
    def update_view(self):
        """Update the view based on current settings"""
        self.render_tasks()
        
    def on_search_change(self, *args):
        """Handle search input changes"""
        search_term = self.search_var.get().lower()
        if not search_term:
            self.render_tasks()
            return
            
        
        all_tasks = self.task_list.get_all_tasks() + self.completed_tasks.get_all_tasks()
        filtered = [t for t in all_tasks if search_term in t.content.lower() or 
                   any(search_term in tag.lower() for tag in t.tags)]
                   
        
        for widget in self.task_container.winfo_children():
            widget.destroy()
            
        
        if not filtered:
            ttk.Label(
                self.task_container,
                text="No matching tasks found",
                font=("Roboto", 12),
                bootstyle=SECONDARY
            ).pack(pady=50)
        else:
            for task in filtered:
                if task.completion_time:
                    self.create_completed_card(self.task_container, task)
                else:
                    self.create_task_card(self.task_container, task)
                    
    def on_entry_focus_in(self, event):
        """Handle focus in event for task entry"""
        if self.task_var.get() == "Add a new task...":
            self.task_var.set("")
            
    def on_entry_focus_out(self, event):
        """Handle focus out event for task entry"""
        if not self.task_var.get().strip():
            self.task_var.set("Add a new task...")
            
    def change_heading(self, event):
        """Allow changing the app heading"""
        new_heading = simpledialog.askstring(
            "Change Heading",
            "Enter new heading:",
            initialvalue=self.heading_text.get(),
            parent=self.root
        )
        if new_heading:
            self.heading_text.set(new_heading)
            
    def toggle_dark_mode(self):
        """Toggle between dark and light mode"""
        if self.dark_mode.get():
            self.style.theme_use("superhero")  
        else:
            self.style.theme_use("flatly")    
            
    def import_data(self):
        """Import tasks from JSON file"""
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="Select file to import"
        )
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    
                
                self.task_list = TaskLinkedList()
                self.completed_tasks = TaskLinkedList()
                self.task_tree = TaskTree()
                
                
                for task_data in data.get("tasks", []):
                    task = Task.from_dict(task_data)
                    self.task_list.append(task)
                    
                for task_data in data.get("completed", []):
                    task = Task.from_dict(task_data)
                    self.completed_tasks.append(task)
                    
                
                for category, tasks in data.get("categories", {}).items():
                    for task_data in tasks:
                        task = Task.from_dict(task_data)
                        self.task_tree.add_task_to_category(category, task)
                        
                messagebox.showinfo("Import Successful", "Tasks imported successfully!")
                self.render_tasks()
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import tasks: {str(e)}")
                
    def export_data(self):
        """Export tasks to JSON file"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Save tasks to file"
        )
        if filepath:
            try:
                data = {
                    "tasks": [t.to_dict() for t in self.task_list.get_all_tasks()],
                    "completed": [t.to_dict() for t in self.completed_tasks.get_all_tasks()],
                    "categories": {}
                }
                
                
                for path, task in self.task_tree.dfs_traverse():
                    if path != "Root":
                        if path not in data["categories"]:
                            data["categories"][path] = []
                        data["categories"][path].append(task.to_dict())
                        
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                    
                messagebox.showinfo("Export Successful", "Tasks exported successfully!")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export tasks: {str(e)}")
                
    def load_data(self):
        """Load tasks from default data file"""
        try:
            if os.path.exists("tasks.json"):
                with open("tasks.json", 'r') as f:
                    data = json.load(f)
                    
                for task_data in data.get("tasks", []):
                    task = Task.from_dict(task_data)
                    self.task_list.append(task)
                    
                for task_data in data.get("completed", []):
                    task = Task.from_dict(task_data)
                    self.completed_tasks.append(task)
                    
                for category, tasks in data.get("categories", {}).items():
                    for task_data in tasks:
                        task = Task.from_dict(task_data)
                        self.task_tree.add_task_to_category(category, task)
        except Exception as e:
            print(f"Error loading data: {e}")
            
    def save_data(self):
        """Save tasks to default data file"""
        try:
            data = {
                "tasks": [t.to_dict() for t in self.task_list.get_all_tasks()],
                "completed": [t.to_dict() for t in self.completed_tasks.get_all_tasks()],
                "categories": {}
            }
            
            for path, task in self.task_tree.dfs_traverse():
                if path != "Root":
                    if path not in data["categories"]:
                        data["categories"][path] = []
                    data["categories"][path].append(task.to_dict())
                    
            with open("tasks.json", 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
            
    def on_closing(self):
        """Handle window closing event"""
        self.save_data()
        self.root.destroy()


def main():
    root = ttk.Window()
    app = ModernTodoApp(root)
    
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()


if __name__ == "__main__":
    main()
