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
from datetime import datetime, date


# Classes

class Task:
    def __init__(self, task_id, task_name, created_date, deadline_date, status):
        self.task_id = task_id
        self.task_name = task_name
        self.created_date = created_date
        self.deadline_date = deadline_date
        self.status = status

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
    status = status_var.get()
    deadline_date = cal_entry.get()
    deadline_time = set_time().strip()

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
    # Clear previous data
    for row in treeview.get_children():
        treeview.delete(row)

    c.execute("SELECT * FROM tasks")
    tasks = c.fetchall()

    for task in tasks:
        curr_date = datetime.now().replace(second=0, microsecond=0)
        deadline_date = datetime.strptime(task[3], '%d/%m/%Y %H:%M')
        if curr_date > deadline_date:
            task = list(task)
            task[4] = "Expired"
            task = tuple(task)
            treeview.insert("", "end", values=task, tags=("expired",))
        else:
            treeview.insert("", "end", values=task)

    treeview.tag_configure("expired", foreground="red")
    treeview.bind("<Motion>", on_treeview_hover)
    treeview.bind("<Double-1>", on_treeview_click)

def on_treeview_click(event):
    tree = event.widget
    item = tree.identify_row(event.y)
    task = tree.item(item)['values']
    show_task_info(task)
    # print(task)


def show_task_info(task):
    info_box = tk.Toplevel()
    info_box.title("Task Information")
    info_box.geometry('530x300')
    info_box.resizable(False, False)

    # Task info functions
    def back_to_task_list():
        show_task_list()
        info_box.destroy()

    def save_task():
        if done_var.get():
            task_name = current_task_name.get().strip()
            status = ('Task Completed')
            deadline_date = current_task_deadline_date.get()

            if not (task_name and status and deadline_date):
                showinfo(title='Error', message='Please fill in all fields.')
                return

            c.execute('''UPDATE tasks 
                                     SET task_name=?, deadline_date=?, status=? 
                                     WHERE id=?''', (task_name, deadline_date, status, current_task.task_id))
            conn.commit()

            showinfo(title='Success', message='Task Completed!')
            back_to_task_list()
        else:
            task_name = current_task_name.get().strip()
            status = current_task_status.get()
            deadline_date = current_task_deadline_date.get()

            if not (task_name and status and deadline_date):
                showinfo(title='Error', message='Please fill in all fields.')
                return

            c.execute('''UPDATE tasks 
                         SET task_name=?, deadline_date=?, status=? 
                         WHERE id=?''', (task_name, deadline_date, status, current_task.task_id))
            conn.commit()

            showinfo(title='Success', message='Task updated successfully!')
            back_to_task_list()

    def delete_task():
        c.execute("DELETE FROM tasks WHERE id=?", (current_task.task_id,))
        conn.commit()
        showinfo(title='Success', message='Task deleted successfully!')
        back_to_task_list()

    def task_done():
        if done_var.get():
            current_task_name.config(state=tk.DISABLED)
            current_task_status.config(state=tk.DISABLED)
            current_task_deadline_date.config(state=tk.DISABLED)
            current_task_creation_date.config(state=tk.DISABLED)
        else:
            current_task_name.config(state=tk.NORMAL)
            current_task_status.config(state=tk.NORMAL)
            current_task_deadline_date.config(state=tk.NORMAL)
            current_task_creation_date.config(state=tk.NORMAL)

    # Right Frame position
    right_frame.update_idletasks()
    right_frame_width = right_frame.winfo_width()
    right_frame_height = right_frame.winfo_height()
    right_frame_x = right_frame.winfo_rootx()
    right_frame_y = right_frame.winfo_rooty()

    # Set center for info_box
    info_box_width = info_box.winfo_width()
    info_box_height = info_box.winfo_height()
    x = right_frame_x + (right_frame_width - info_box_width) // 2
    y = right_frame_y + (right_frame_height - info_box_height) // 2
    info_box.geometry('+{}+{}'.format(x, y))

    # Get info and make obj
    current_task = Task(task[0], task[1], task[2], task[3], task[4])

    # Chekbox variable

    done_var = tk.BooleanVar()
    done_var.set(False)

    # Make interface
    ttk.Label(info_box, text='Task ID: ', anchor="e").grid(column=0, row=0, pady=20, padx=(10, 5), sticky=tk.E)
    ttk.Label(info_box, text=current_task.task_id, anchor="w").grid(column=1, row=0, sticky='w')

    ttk.Checkbutton(info_box, text="Task Completed", command=task_done, variable=done_var).grid(column=4, row=0, sticky=tk.E)

    ttk.Label(info_box, text='Task Name: ', anchor="e").grid(column=0, row=1, pady=5, padx=(10, 5), sticky=tk.E)
    current_task_name = ttk.Entry(info_box)
    current_task_name.grid(column=1, row=1, columnspan=4, sticky='ew')
    current_task_name.insert(tk.END, current_task.task_name)

    ttk.Label(info_box, text='Creation Date: ', anchor="e").grid(column=0, row=2, pady=5, padx=(10, 5), sticky=tk.E)
    current_task_creation_date = ttk.Entry(info_box)
    current_task_creation_date.grid(column=1, row=2, sticky='ew')
    current_task_creation_date.insert(tk.END, current_task.created_date)

    ttk.Label(info_box, text='Deadline Date: ', anchor="e").grid(column=3, row=2,pady=5, padx=5, sticky=tk.E)
    current_task_deadline_date = ttk.Entry(info_box)
    current_task_deadline_date.grid(column=4, row=2, sticky='ew')
    current_task_deadline_date.insert(tk.END, current_task.deadline_date)

    ttk.Label(info_box, text='Status: ', anchor="e").grid(column=0, row=3, sticky=tk.E)
    current_task_status = ttk.Combobox(info_box, values=("Need to do", "Already done", "In process"))
    current_task_status.grid(column=1, row=3, sticky='ew')
    current_task_status.insert(tk.END, current_task.status)

    # Buttons
    ttk.Button(info_box, text='Back', command=back_to_task_list).grid(column=0, row=4, pady=(100, 5), padx=10,sticky=tk.EW)
    ttk.Button(info_box, text='Save task', command=save_task).grid(column=1, row=4, pady=(100, 5), sticky=tk.EW)
    ttk.Button(info_box, text='Delete task', command=delete_task).grid(column=4, row=4, pady=(100, 5), sticky=tk.EW)

    task_done()


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


def on_treeview_hover(event):
    tree = event.widget
    item = tree.identify_row(event.y)
    tree.tk.call(tree, "tag", "remove", "highlight")
    tree.tk.call(tree, "tag", "add", "highlight", item)


def update_time():
    current_time = datetime.now().strftime('%H:%M')
    current_data = datetime.now().strftime('%A, %B %d, %Y')
    stat_fig3_label.config(text=f"Today is :\n{current_data}\n{current_time}")
    right_frame.after(1000, update_time)


def set_time():
    hours, minutes = time_picker.time()[0], time_picker.time()[1]
    formatted_time = "{:02d}:{:02d}".format(hours, minutes)
    time_picker.pack_forget()
    return formatted_time


def show_picked_date(event=None):
    date_str = cal.get_date()
    cal_entry.delete(0, tk.END)
    cal_entry.insert(tk.END, date_str)
    selected_date = datetime.strptime(date_str, '%d/%m/%Y').date()
    current_date = date.today()

    if selected_date < current_date:
        cal_entry.config(fg="red")
    else:
        cal_entry.config(fg="black")

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
title_label = tk.Label(right_frame_title, text="Task list", font=("Helvetica", 20, 'bold'), bg="white", fg="#50C878")
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
search_bar = ttk.Entry(search_bar_frame, width=30, font=18, background="white")
search_bar.insert(tk.END, "Find a task")
search_bar.grid(row=2, column=0, pady=10, padx=(15, 0), sticky=tk.W)

filter_bar = ttk.Combobox(search_bar_frame, values=("Need to do", "Already done", "In process", "Expired"))
filter_bar_label = tk.Label(search_bar_frame, text="Filter by: ", background="white")
filter_bar_label.grid(row=2, column=1, padx=(10, 0), pady=20, sticky=tk.W)
filter_bar.grid(row=2, column=2, pady=10, sticky=tk.W)

sort_bar = ttk.Combobox(search_bar_frame, values=("Id", "Alphabetic", "Status", "Date: Created", "Date: Deadline"))
sort_bar_label = tk.Label(search_bar_frame, text="Sort by: ", background="white")
sort_bar_label.grid(row=2, column=3, padx=(10, 0), pady=20, sticky=tk.W)
sort_bar.grid(row=2, column=4, pady=10, sticky=tk.W)

update_btn_img = ImageTk.PhotoImage(Image.open("update.png").resize((20, 20), Image.LANCZOS))
update_btn = ttk.Button(search_bar_frame, image=update_btn_img, command=lambda: (load_tasks(), task_counter()))
update_btn.grid(row=2, column=5, padx=15, pady=10, sticky=tk.W)
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
treeview.column("Task", width=505, anchor=tk.CENTER)
treeview.heading("Created", text="Created")
treeview.column("Created", width=150, anchor=tk.CENTER)
treeview.heading("Deadline date", text="Deadline date")
treeview.column("Deadline date", width=150, anchor=tk.CENTER)
treeview.heading("Status", text="Status")
treeview.column("Status", width=100, anchor=tk.CENTER)
treeview.tag_configure('highlight', background='lightblue')
treeview.bind("<Motion>", on_treeview_hover)
treeview.bind('<Double-1>', on_treeview_click)
# Data from db
load_tasks()

task_counter()
treeview.grid(row=3, column=0, columnspan=4, padx=(15, 0), pady=20)

# Treeview scrollbar
scrollbar = tk.Scrollbar(treeview_frame, orient="vertical", command=treeview.yview)
treeview.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=3, column=4, sticky="ns", pady=20)
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
task_name_frame.pack()

# Status Frame
status_var = tk.StringVar()
status_frame = tk.Frame(create_task_frame, bg="#fafafa")
status_frame_label = tk.Label(status_frame, text="Choose a task status:", font=("Helvetica", 12), bg="#fafafa")
status_frame_label.grid(row=1, column=0, padx=10, pady=10)
R1 = ttk.Radiobutton(status_frame, text="Need to do", value='Need to do', variable=status_var)
R2 = ttk.Radiobutton(status_frame, text="Already done", value='Already done', variable=status_var)
R3 = ttk.Radiobutton(status_frame, text="In process", value='In process', variable=status_var)
R4 = ttk.Radiobutton(status_frame, text="Expired", value='Expired', variable=status_var)
R1.grid(row=1, column=1, padx=10, pady=10, sticky='ws')
R2.grid(row=1, column=2, padx=10, pady=10, sticky='w')
R3.grid(row=1, column=3, padx=10, pady=10, sticky='w')
R4.grid(row=1, column=4, padx=10, pady=10, sticky='w')
status_frame.pack(fill=tk.BOTH, expand=True, pady=(50, 0), padx=10)

# Deadline Frame
deadline_frame = tk.Frame(create_task_frame, bg="white", pady=10)
deadline_label = tk.Label(deadline_frame, text="Set a deadline time and date:", font=("Helvetica", 12), bg="white")
deadline_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

# Time picker
time_picker = SpinTimePickerModern(deadline_frame)
time_picker_label = tk.Label(deadline_frame, text="Set a time: ", font=("Helvetica", 12), bg="white")
time_picker_label.grid(row=1, column=0, padx=(10, 0), pady=10, sticky='w')
time_picker.addAll(constants.HOURS24)
time_picker.configureAll(bg="white", fg="#333333", font=("Arial", 12), hoverbg="#CCCCCC",
                         hovercolor="#333333", clickedbg="#50C878", clickedcolor="white")
time_picker.grid(row=1, column=1, columnspan=4, pady=10)
deadline_frame.pack(fill=tk.BOTH, expand=True)

# Calendar
cal = Calendar(create_task_frame, date_pattern='dd/MM/yyyy', font="Arial 12", cursor='hand2', locale='en_US')
cal.config(background="#50C878", selectbackground="#fafafa", selectforeground="green")
cal.bind("<<CalendarSelected>>", show_picked_date)
cal_entry = tk.Entry(cal, width=9, font=("Helvetica", 12),)
cal_label = tk.Label(create_task_frame, text="Choose a date:", font=("Helvetica", 12), bg="white")
cal_label.pack(padx=10, pady=10, anchor=tk.W)
cal_entry.pack(padx=10, pady=10, anchor=tk.W)
cal.pack(fill=tk.BOTH, padx=10, pady=0)


# Buttons Frame

create_btn_style = ttk.Style()
create_btn_style.theme_use('alt')
treeview_style.configure("TButton", background="#50C878", fg="white")

buttons_frame = tk.Frame(create_task_frame, background="white")
back_button = ttk.Button(buttons_frame, text="Back", width=20, command=show_task_list)
back_button.grid(row=0, column=0, padx=10, pady=10)
create_button = ttk.Button(buttons_frame, text="Create", width=20, style="TButton", command=save_task)
create_button.grid(row=0, column=1, padx=10, pady=10)
buttons_frame.pack(fill=tk.BOTH, expand=True, pady=(100, 10))


create_task_frame.pack(fill=tk.BOTH, expand=True)


sv_ttk.set_theme("light")
app.mainloop()
