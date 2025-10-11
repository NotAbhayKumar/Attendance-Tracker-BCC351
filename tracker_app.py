import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os

# --- 1. CONFIGURATION & STYLING ---
DATA_FILE = "attendance_pro_data.json"
BG_COLOR = "#2E3440"
FRAME_COLOR = "#3B4252"
TEXT_COLOR = "#ECEFF4"
ACCENT_COLOR = "#88C0D0"
SUCCESS_COLOR = "#A3BE8C"
DANGER_COLOR = "#BF616A"
FONT_FAMILY = "Segoe UI"

# --- 2. BACKEND LOGIC ---
def load_data():
    """Loads all app data (subjects and settings) from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return {"subjects": {}, "settings": {"goal": 75.0}}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, KeyError):
        return {"subjects": {}, "settings": {"goal": 75.0}}

def save_data(data):
    """Saves all app data to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- 3. GUI APPLICATION ---
class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pro Attendance Tracker")
        self.root.geometry("600x600")
        self.root.configure(bg=BG_COLOR)

        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background=FRAME_COLOR)
        style.configure("TLabel", background=FRAME_COLOR, foreground=TEXT_COLOR, font=(FONT_FAMILY, 11))
        style.configure("TButton", background=ACCENT_COLOR, foreground=BG_COLOR, font=(FONT_FAMILY, 10, "bold"))
        style.map("TButton", background=[('active', '#96d1e3')])
        style.configure("TEntry", fieldbackground="#4C566A", foreground=TEXT_COLOR, insertcolor=TEXT_COLOR)

        self.app_data = load_data()
        self.attendance_goal = tk.DoubleVar(value=self.app_data["settings"]["goal"])

        self.create_menu()

        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill="both", expand=True)

        add_frame = ttk.Frame(main_frame, padding="10")
        add_frame.pack(fill="x")
        
        ttk.Label(add_frame, text="Subject Name:").pack(side="left", padx=(0, 5))
        self.subject_entry = ttk.Entry(add_frame, font=(FONT_FAMILY, 11))
        self.subject_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(add_frame, text="Add Subject", command=self.add_subject).pack(side="left", padx=(10, 5))
        
        # --- NEW: Delete button added here ---
        ttk.Button(add_frame, text="Delete Subject", command=self.delete_subject, style="Danger.TButton").pack(side="left")
        
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill="both", expand=True, pady=10)
        self.subject_listbox = tk.Listbox(list_frame, bg="#4C566A", fg=TEXT_COLOR, font=(FONT_FAMILY, 12),
                                          selectbackground=ACCENT_COLOR, selectforeground=BG_COLOR, borderwidth=0, highlightthickness=0)
        self.subject_listbox.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.subject_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.subject_listbox.config(yscrollcommand=scrollbar.set)

        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x")
        
        ttk.Button(action_frame, text="Mark Attended", command=self.mark_attended, style="Success.TButton").pack(side="left", expand=True, padx=2)
        ttk.Button(action_frame, text="Mark Missed", command=self.mark_missed, style="Danger.TButton").pack(side="left", expand=True, padx=2)
        ttk.Button(action_frame, text="Edit Selected", command=self.open_edit_window).pack(side="left", expand=True, padx=2)
        
        style.configure("Success.TButton", background=SUCCESS_COLOR, foreground=BG_COLOR, font=(FONT_FAMILY, 10, "bold"))
        style.configure("Danger.TButton", background=DANGER_COLOR, foreground=TEXT_COLOR, font=(FONT_FAMILY, 10, "bold"))
        
        self.refresh_listbox()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Set Attendance Goal...", command=self.set_goal)
        file_menu.add_separator()
        file_menu.add_command(label="Reset All Data", command=self.reset_all_data)
        file_menu.add_command(label="Exit", command=self.root.quit)

    def refresh_listbox(self):
        self.subject_listbox.delete(0, tk.END)
        subjects = self.app_data["subjects"]
        goal = self.attendance_goal.get() / 100.0

        if not subjects:
            self.subject_listbox.insert(tk.END, "Add a subject to begin!")
            return

        for subject, data in sorted(subjects.items()):
            total, attended = data.get('total', 0), data.get('attended', 0)
            
            if total == 0:
                percentage = 100.0
                status_msg = "No classes held yet."
            else:
                percentage = (attended / total) * 100
                if percentage >= goal * 100:
                    can_miss = int((attended - (goal * total)) / goal)
                    status_msg = f"✅ Safe. You can miss the next {can_miss} classes."
                else:
                    needed = -(-((goal * total) - attended) // (1 - goal))
                    status_msg = f"⚠️ Danger! Must attend the next {int(needed)} classes."

            display_text = f"{subject}  |  {attended}/{total}  |  {percentage:.2f}%"
            self.subject_listbox.insert(tk.END, display_text)
            self.subject_listbox.insert(tk.END, f"  └ {status_msg}\n")

    def get_selected_subject(self):
        try:
            selected_index = self.subject_listbox.curselection()[0]
            if selected_index % 2 != 0:
                selected_index -= 1
            
            selected_text = self.subject_listbox.get(selected_index)
            subject_name = selected_text.split('|')[0].strip()
            return subject_name
        except IndexError:
            messagebox.showwarning("No Selection", "Please select a subject from the list.")
            return None

    def add_subject(self):
        subject_name = self.subject_entry.get().strip()
        if subject_name and subject_name not in self.app_data["subjects"]:
            self.app_data["subjects"][subject_name] = {"attended": 0, "total": 0}
            save_data(self.app_data)
            self.refresh_listbox()
            self.subject_entry.delete(0, tk.END)
        elif not subject_name:
            messagebox.showerror("Error", "Subject name cannot be empty.")
        else:
            messagebox.showinfo("Info", "Subject already exists.")

    # --- NEW: Function to handle subject deletion ---
    def delete_subject(self):
        """Deletes the selected subject after confirmation."""
        subject_name = self.get_selected_subject()
        if subject_name:
            # Show a confirmation box before deleting
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete '{subject_name}'?"):
                del self.app_data["subjects"][subject_name]
                save_data(self.app_data)
                self.refresh_listbox()

    def mark_attended(self):
        subject = self.get_selected_subject()
        if subject:
            self.app_data["subjects"][subject]['attended'] += 1
            self.app_data["subjects"][subject]['total'] += 1
            save_data(self.app_data)
            self.refresh_listbox()

    def mark_missed(self):
        subject = self.get_selected_subject()
        if subject:
            self.app_data["subjects"][subject]['total'] += 1
            save_data(self.app_data)
            self.refresh_listbox()
            
    def open_edit_window(self):
        subject = self.get_selected_subject()
        if not subject:
            return

        edit_win = tk.Toplevel(self.root)
        edit_win.title(f"Edit {subject}")
        edit_win.configure(bg=FRAME_COLOR)
        
        data = self.app_data["subjects"][subject]
        
        ttk.Label(edit_win, text="Classes Attended:", padding=5).grid(row=0, column=0, sticky="w")
        attended_entry = ttk.Entry(edit_win)
        attended_entry.grid(row=0, column=1, padx=5, pady=5)
        attended_entry.insert(0, data["attended"])

        ttk.Label(edit_win, text="Total Classes Held:", padding=5).grid(row=1, column=0, sticky="w")
        total_entry = ttk.Entry(edit_win)
        total_entry.grid(row=1, column=1, padx=5, pady=5)
        total_entry.insert(0, data["total"])

        def save_changes():
            try:
                new_attended = int(attended_entry.get())
                new_total = int(total_entry.get())
                if new_attended > new_total or new_attended < 0 or new_total < 0:
                    messagebox.showerror("Invalid Input", "Values are not logical.", parent=edit_win)
                    return
                
                self.app_data["subjects"][subject]["attended"] = new_attended
                self.app_data["subjects"][subject]["total"] = new_total
                save_data(self.app_data)
                self.refresh_listbox()
                edit_win.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numbers.", parent=edit_win)

        ttk.Button(edit_win, text="Save", command=save_changes).grid(row=2, column=0, columnspan=2, pady=10)

    def set_goal(self):
        new_goal = simpledialog.askfloat("Set Goal", "Enter new attendance goal (%):",
                                         parent=self.root,
                                         initialvalue=self.attendance_goal.get(),
                                         minvalue=1.0, maxvalue=100.0)
        if new_goal:
            self.attendance_goal.set(new_goal)
            self.app_data["settings"]["goal"] = new_goal
            save_data(self.app_data)
            self.refresh_listbox()

    def reset_all_data(self):
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to delete ALL subjects?\nThis cannot be undone."):
            self.app_data["subjects"] = {}
            save_data(self.app_data)
            self.refresh_listbox()

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()