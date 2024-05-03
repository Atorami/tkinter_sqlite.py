import tkinter as tk
from tkinter.messagebox import showinfo

import sv_ttk
import sqlite3
from tkinter import ttk
from tkcalendar import Calendar
from tktimepicker import SpinTimePickerModern
from tktimepicker import constants
from tkinter import filedialog
from tkinter import messagebox

from PIL import ImageTk, Image
from datetime import datetime


# SQLite and Functions
conn = sqlite3.connect('tasks.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                task_name TEXT NOT NULL,
               creation_date TEXT NOT NULL,
                deadline_date TEXT NOT NULL,
                 status TEXT NOT NULL
            )''')
conn.commit()


def save_task():
    # Get all entry data
    task_name = task_name_entry.get().strip()
    status = status_var.get().strip()
    deadline_date = deadline_entry.get().strip()
    deadline_time = deadline_entry_time.get().strip()

    # Check if all fields are filled
    if not (task_name and status and deadline_date and deadline_time):
        showinfo(title='Error', message='Please fill in all fields.')
        return

    # Combine deadline date and time
    deadline_datetime = datetime.strptime(deadline_date, '%d/%m/%Y')
    deadline_time = datetime.strptime(deadline_time, '%H:%M')
    deadline_datetime = deadline_datetime.replace(hour=deadline_time.hour, minute=deadline_time.minute)
    deadline_date_formatted = deadline_datetime.strftime('%d/%m/%Y %H:%M')

    # Get current date and time
    creation_date = datetime.now().strftime('%d/%m/%Y %H:%M')

    # Insert data into the database
    c.execute('''INSERT INTO tasks (task_name, creation_date, deadline_date, status)
                 VALUES (?, ?, ?, ?)''', (task_name, creation_date, deadline_date_formatted, status))
    conn.commit()

    showinfo(title='Success', message='Task added successfully!')


def load_tasks():
    # Clear prev data
    for row in treeview.get_children():
        treeview.delete(row)

    c.execute("SELECT * FROM tasks")
    tasks = c.fetchall()

    for task in tasks:
        treeview.insert("", "end", values=task)




# Functions


def show_task_list():
    right_frame.pack(fill=tk.BOTH, expand=True)
    create_task_frame.pack_forget()


def show_task_creator():
    create_task_frame.pack(fill=tk.BOTH, expand=True)
    right_frame.pack_forget()


def task_counter():
    task_number = 0
    for row in treeview.get_children():
        task_number += 1

    stat_fig1_label.config(text=f"Tasks: {task_number}")


def update_time():
    current_time = datetime.now().strftime('%H:%M')
    current_data = datetime.now().strftime('%A, %B %d, %Y')
    stat_fig3_label.config(text=f"Today is :\n{current_data}\n{current_time}")
    right_frame.after(1000, update_time)


def open_calendar():
    cal = Calendar(create_task_frame, date_pattern='dd/MM/yyyy', font="Arial 14", selectbackground='gray80', locale='en_US')
    cal.pack(fill='both', expand=True)

    def set_date():
        deadline_entry.delete(0, 'end')
        deadline_entry.insert(0, cal.get_date())
        cal.pack_forget()
        ok_button.pack_forget()

    ok_button = ttk.Button(create_task_frame, text="OK", command=set_date)
    ok_button.pack(fill=tk.X)


def open_timepicker():
    time_picker = SpinTimePickerModern(create_task_frame)
    time_picker.addAll(constants.HOURS24)
    time_picker.configureAll(bg="#50C878", fg="#ffffff", height=3, width=15, font=("Arial", 24), hoverbg="#3CB371",
                             hovercolor="#ffffff", clickedbg="#2E8B57", clickedcolor="#ffffff")
    time_picker.configure_separator(bg="#50C878", fg="#ffffff", font=("Arial", 50))

    time_picker.pack(expand=True)

    def set_time():
        deadline_entry_time.delete(0, 'end')
        hours, minutes = time_picker.time()[0], time_picker.time()[1]
        formatted_time = "{:02d}:{:02d}".format(hours, minutes)
        deadline_entry_time.insert(0, formatted_time)
        time_picker.pack_forget()
        time_ok_button.pack_forget()

    time_ok_button = ttk.Button(create_task_frame, text="OK", command=set_time)
    time_ok_button.pack(fill="both")




# APP

app = tk.Tk()
app.title("Task Manager")
app.geometry("1366x768")
app.resizable(False, False)

main_frame = ttk.Frame(app)
main_frame.pack(fill="both", expand=False)

# Left frame
left_frame = tk.Frame(main_frame, width=350, height=768, background="#50C878", bd=0)
left_frame.pack_propagate(0)
left_frame.pack(side=tk.LEFT, fill=tk.Y)

# Logo
logo = Image.open("task_logo.png").resize((100, 100), Image.LANCZOS)
logo_tk = ImageTk.PhotoImage(logo)
logo_label = tk.Label(left_frame, image=logo_tk, bg="#50C878")
logo_label.pack(pady=50)

# Menu
menu_frame = tk.Frame(left_frame, width=350, background="#50C878")
menu_btn1 = tk.Button(menu_frame, text="Task list", width=30, height=2, fg='#50C878', bd=0, font=16, command=show_task_list)
menu_btn1.pack(padx=10)
menu_btn2 = tk.Button(menu_frame, text="Task creator", width=30, height=2, fg='#50C878', bd=0, font=16, command=show_task_creator)
menu_btn2.pack(padx=10, pady=10)
menu_btn3 = tk.Button(menu_frame, text="Settings", width=30, height=2, fg='#50C878', bd=0, font=16)
menu_btn3.pack(padx=10, pady=10)
menu_frame.pack(pady=50)

# Right frame

# Task List Frame
right_frame = tk.Frame(main_frame, background="white")
right_frame.pack_propagate(0)
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Right frame title
right_frame_title = tk.Frame(right_frame, background="white")
title_label = tk.Label(right_frame_title, text="Task list", font=("Helvetica", 20), bg="white", fg="#50C878")
title_label.pack(padx=15, pady=15, anchor=tk.W)
right_frame_title.pack(fill=tk.X)

# Stat figures
stat_fig_frame = tk.Frame(right_frame, background="white")
stat_fig1_label = tk.Label(stat_fig_frame, width=25, height=4, text=f"Tasks: 0", font=18, background="#50C878", fg="white")
stat_fig1_label.grid(row=1, column=0, padx=15, pady=20, sticky=tk.W)

stat_fig2_label = tk.Label(stat_fig_frame, width=25, height=4, text="Tasks done: 10", font=18, background="#50C878", fg="white")
stat_fig2_label.grid(row=1, column=1, padx=10, pady=20, sticky=tk.W)

stat_fig3_label = tk.Label(stat_fig_frame, width=53, height=4, text="Current time: ", font=18, background="#50C878", fg="white")
stat_fig3_label.grid(row=1, column=2, padx=10, pady=20, sticky=tk.W)
stat_fig_frame.pack(fill=tk.X)

# Search bar and filters
search_bar_frame = tk.Frame(right_frame, background="white")
search_bar = ttk.Entry(search_bar_frame, width=34, font=18, background="white")
search_bar.insert(tk.END, "Find a task")
search_bar.grid(row=2, column=0, pady=10, padx=15, sticky=tk.W)

filter_bar = ttk.Combobox(search_bar_frame, values=("Done", "Not done"))
filter_bar.grid(row=2, column=1, padx=15, pady=10, sticky=tk.W)

sort_bar = ttk.Combobox(search_bar_frame, values=("Id", "Alphabetic", "Status", "Date"))
sort_bar.grid(row=2, column=2, padx=15, pady=10, sticky=tk.W)

update_btn_img = ImageTk.PhotoImage(Image.open("update.png").resize((20, 20), Image.LANCZOS))
update_btn = ttk.Button(search_bar_frame, image=update_btn_img, command=lambda: (load_tasks(), task_counter()))
update_btn.grid(row=2, column=3, padx=15, pady=10, sticky=tk.W)
search_bar_frame.pack(fill=tk.X)

# Treeview tasks
    # Treeview styling
treeview_style = ttk.Style()
treeview_style.configure("Treeview.Heading", background="white")

treeview_frame = tk.Frame(right_frame, background="white")
treeview = ttk.Treeview(treeview_frame, columns=("ID", "Task", "Created", "Deadline date", "Status"), show="headings", height=22, style="Treeview.Heading")
treeview.heading("ID", text="ID")
treeview.column("ID", width=50, anchor=tk.CENTER)
treeview.heading("Task", text="Task")
treeview.column("Task", width=400, anchor=tk.CENTER)
treeview.heading("Created", text="Created")
treeview.column("Created", width=150, anchor=tk.CENTER)
treeview.heading("Deadline date", text="Deadline date")
treeview.column("Deadline date", width=150, anchor=tk.CENTER)
treeview.heading("Status", text="Status")
treeview.column("Status", width=100, anchor=tk.CENTER)

# Data from db
load_tasks()
task_counter()
treeview.grid(row=3, column=0, columnspan=4, padx=15, pady=20)

# Treeview scrollbar
scrollbar = tk.Scrollbar(treeview_frame, orient="vertical", command=treeview.yview)
treeview.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=3, column=4, sticky="ns")
treeview_frame.pack(fill=tk.BOTH, expand=True)

update_time()

# Create Task Frame

create_task_frame = tk.Frame(main_frame, background="white")
right_frame.pack_propagate(0)
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Right Task Frame Title
create_task_frame_title = tk.Frame(create_task_frame, background="white")
create_task_title_label = tk.Label(create_task_frame_title, text="Create task", font=("Helvetica", 20, 'bold'), bg="white", fg="#50C878")
create_task_title_label.pack(padx=15, pady=15, anchor=tk.W)
create_task_frame_title.pack(fill=tk.X)

# Right Task Entry for Task Name
task_name_frame = tk.Frame(create_task_frame, background="white")
task_name_label = tk.Label(task_name_frame, text="Task Name:", font=("Helvetica", 12), bg="white")
task_name_label.grid(row=0, column=0, padx=10, pady=10)

task_name_entry = ttk.Entry(task_name_frame, width=108, font=("Helvetica", 12))
task_name_entry.grid(row=1, column=0, padx=10, sticky=tk.W)
task_name_frame.pack(fill=tk.X)

# Deadline Frame

deadline_frame = tk.Frame(create_task_frame, background="white")
deadline_label = tk.Label(deadline_frame, text="Deadline:", font=("Helvetica", 12), bg="white")
deadline_label.grid(row=0, column=0, padx=10, pady=10)

deadline_entry = ttk.Entry(deadline_frame, width=20, font=("Helvetica", 12))
deadline_entry.grid(row=1, column=0, padx=10, pady=10)

deadline_calendar_button = ttk.Button(deadline_frame, text="Open Calendar", command=open_calendar)
deadline_calendar_button.grid(row=1, column=1, padx=10, pady=10)

deadline_entry_time = ttk.Entry(deadline_frame, width=20, font=("Helvetica", 12))
deadline_entry_time.grid(row=2, column=0, padx=10, pady=10)

deadline_entry_time_button = ttk.Button(deadline_frame, text="Open Timepicker", command=open_timepicker)
deadline_entry_time_button.grid(row=2, column=1, padx=10, pady=10)

deadline_frame.pack(fill=tk.X)

# Status Frame
status_frame = tk.Frame(create_task_frame, background="white")
status_label = tk.Label(status_frame, text="Status:", font=("Helvetica", 12), bg="white")
status_label.grid(row=0, column=0, padx=10, pady=10)

status_var = tk.StringVar()
status_dropdown = ttk.Combobox(status_frame, textvariable=status_var, values=["To Do", "In Progress", "Completed"], width=20, font=("Helvetica", 12))
status_dropdown.grid(row=1, column=0, padx=10, pady=10)
status_dropdown.current(0)
status_frame.pack(fill=tk.X)

# Buttons Frame

create_btn_style = ttk.Style()
create_btn_style.theme_use('alt')
treeview_style.configure("TButton", background="#50C878", fg="white")

buttons_frame = tk.Frame(create_task_frame, background="white")
back_button = ttk.Button(buttons_frame, text="Back", width=20, command=show_task_list)
back_button.grid(row=0, column=0, padx=10, pady=10)
create_button = ttk.Button(buttons_frame, text="Create", width=20, style="TButton", command=save_task)
create_button.grid(row=0, column=1, padx=10, pady=10)
buttons_frame.pack(fill=tk.X)




















sv_ttk.set_theme("light")
app.mainloop()
