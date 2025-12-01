# attendance_custom_students.py
import json
import os
import tkinter as tk
from tkinter import messagebox, simpledialog

import customtkinter as ctk

# ---------------- CONFIG ----------------
DATA_FILE = "attendance_pro_data.json"
APP_TITLE = "Pro Attendance Tracker (Students)"
PEACH = "#FFB88C"         # primary accent (peach)
BG_DARK = "#1E1F22"       # background supplement (used minimally)
CARD_BG = "#2A2C2F"       # card background
TEXT_COLOR = "#ECEFF4"
FONT = ("Segoe UI", 11)


# ---------------- Helpers ----------------
def load_data():
    """
    Loads data from JSON. Handles legacy format (top-level 'subjects') by migrating
    into a "Default Student".
    Final shape:
    {
      "students": {
        "Name": {"info": {...}, "subjects": {...}},
        ...
      },
      "settings": {"goal": 75.0}
    }
    """
    if not os.path.exists(DATA_FILE):
        return {"students": {"Default Student": {"info": {}, "subjects": {}}}, "settings": {"goal": 75.0}}
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        # Migration: old format had top-level "subjects"
        if "students" not in data and "subjects" in data:
            migrated = {
                "students": {
                    "Default Student": {
                        "info": {},
                        "subjects": data.get("subjects", {})
                    }
                },
                "settings": data.get("settings", {"goal": 75.0})
            }
            return migrated
        # If current format lacks students key, create safe structure
        if "students" not in data:
            data["students"] = {"Default Student": {"info": {}, "subjects": {}}}
        if "settings" not in data:
            data["settings"] = {"goal": 75.0}
        # Guarantee each student structure has info & subjects
        for s, val in list(data["students"].items()):
            if isinstance(val, dict):
                if "subjects" not in val:
                    val["subjects"] = {}
                if "info" not in val:
                    val["info"] = {}
            else:
                # unexpected shape: replace with empty
                data["students"][s] = {"info": {}, "subjects": {}}
        return data
    except (json.JSONDecodeError, KeyError):
        return {"students": {"Default Student": {"info": {}, "subjects": {}}}, "settings": {"goal": 75.0}}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------- App ----------------
class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("900x700")
        self.root.minsize(760, 560)

        # CustomTkinter appearance & theme
        ctk.set_appearance_mode("dark")       # Dark mode
        ctk.set_default_color_theme("dark-blue")

        self.data = load_data()
        # pick a current student (first one) if exists
        students_list = list(self.data["students"].keys())
        if students_list:
            self.current_student = students_list[0]
        else:
            self.data["students"] = {"Default Student": {"info": {}, "subjects": {}}}
            self.current_student = "Default Student"

        self.goal_percent = tk.DoubleVar(value=self.data["settings"].get("goal", 75.0))
        self.selected_subject = None
        self.card_widgets = {}  # subject -> frame widget

        # Top frame / header
        header = ctk.CTkFrame(self.root, corner_radius=0, fg_color=BG_DARK)
        header.pack(fill="x", side="top")

        title = ctk.CTkLabel(header, text="📘  Pro Attendance Tracker", font=("Segoe UI", 20, "bold"),
                             text_color=PEACH)
        title.pack(side="left", padx=20, pady=14)

        # Right side of header: Student selector & Goal & Menu
        header_right = ctk.CTkFrame(header, fg_color=BG_DARK, corner_radius=0)
        header_right.pack(side="right", padx=12)

        # Student OptionMenu
        self.student_var = tk.StringVar(value=self.current_student)
        students_for_menu = list(self.data["students"].keys())
        self.student_menu = ctk.CTkOptionMenu(header_right, values=students_for_menu,
                                              variable=self.student_var, width=180,
                                              command=self.on_student_change)
        self.student_menu.pack(side="left", padx=(0, 10), pady=10)

        ctk.CTkButton(header_right, text="+ Student", width=100, command=self.add_student_popup,
                      fg_color=PEACH, hover_color="#FFCBA8").pack(side="left", padx=6, pady=8)
        ctk.CTkButton(header_right, text="Delete Student", width=120, command=self.delete_student,
                      fg_color="#BF616A", hover_color="#d26b75").pack(side="left", padx=6, pady=8)

        self.goal_label = ctk.CTkLabel(header_right,
                                       text=f"Goal: {self.goal_percent.get():.0f}%",
                                       font=("Segoe UI", 12, "bold"))
        self.goal_label.pack(side="left", padx=(8, 8), pady=10)

        ctk.CTkButton(header_right, text="Set Goal", width=90, command=self.set_goal,
                      fg_color=PEACH, hover_color="#FFCBA8").pack(side="left", padx=6, pady=8)
        ctk.CTkButton(header_right, text="Reset All", width=90, command=self.reset_all_data,
                      fg_color="#BF616A", hover_color="#d26b75").pack(side="left", padx=6, pady=8)

        # Main area card
        main = ctk.CTkFrame(self.root, corner_radius=12, fg_color=CARD_BG)
        main.pack(fill="both", expand=True, padx=20, pady=18)

        # Add subject row
        add_row = ctk.CTkFrame(main, fg_color=CARD_BG, corner_radius=8)
        add_row.pack(fill="x", padx=12, pady=(12, 8))

        self.entry_subject = ctk.CTkEntry(add_row, placeholder_text="Enter subject name", width=360)
        self.entry_subject.pack(side="left", padx=(6, 8), pady=10)

        ctk.CTkButton(add_row, text="Add Subject", fg_color=PEACH, hover_color="#FFCBA8",
                      command=self.add_subject).pack(side="left", padx=6, pady=8)
        ctk.CTkButton(add_row, text="Delete Selected", fg_color="#BF616A",
                      hover_color="#d26b75", command=self.delete_subject).pack(side="left", padx=6, pady=8)

        # Divider
        divider = ctk.CTkFrame(main, height=1, fg_color="#3B3D40")
        divider.pack(fill="x", padx=12, pady=(4, 8))

        # Scrollable subject list area (cards)
        list_area_frame = ctk.CTkFrame(main, fg_color=CARD_BG)
        list_area_frame.pack(fill="both", expand=True, padx=12, pady=(6, 12))

        self.scrollable = ctk.CTkScrollableFrame(list_area_frame, corner_radius=8, fg_color="#222325",
                                                 width=760)
        self.scrollable.pack(fill="both", expand=True, padx=6, pady=6)

        # Bottom action buttons
        action_row = ctk.CTkFrame(main, fg_color=CARD_BG, corner_radius=8)
        action_row.pack(fill="x", padx=12, pady=(6, 14))

        ctk.CTkButton(action_row, text="✓ Mark Attended", fg_color="#A3BE8C", hover_color="#b6d9b1",
                      command=self.mark_attended).pack(side="left", padx=12, pady=8, expand=True)
        ctk.CTkButton(action_row, text="✗ Mark Missed", fg_color="#BF616A", hover_color="#d26b75",
                      command=self.mark_missed).pack(side="left", padx=12, pady=8, expand=True)
        ctk.CTkButton(action_row, text="Edit Selected", fg_color=PEACH, hover_color="#FFCBA8",
                      command=self.open_edit_window).pack(side="left", padx=12, pady=8, expand=True)

        # Summary footer
        footer = ctk.CTkFrame(self.root, corner_radius=0, fg_color=BG_DARK)
        footer.pack(fill="x", side="bottom")
        self.summary_label = ctk.CTkLabel(footer, text="", anchor="w", font=("Segoe UI", 10))
        self.summary_label.pack(fill="x", padx=18, pady=10)

        # Initial render
        self.render_subject_cards()
        self.update_summary()

    # ---------- Student handling ----------
    def on_student_change(self, value):
        if value in self.data["students"]:
            self.current_student = value
            self.selected_subject = None
            self.clear_selection()
            self.render_subject_cards()
            self.update_summary()

    def add_student_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Add Student")
        popup.geometry("380x220")
        popup.configure(bg=BG_DARK)

        tk.Label(popup, text="Student Name:", bg=BG_DARK, fg=TEXT_COLOR).pack(pady=(12, 4), anchor="w", padx=12)
        ent_name = tk.Entry(popup)
        ent_name.pack(fill="x", padx=12)

        tk.Label(popup, text="Class (optional):", bg=BG_DARK, fg=TEXT_COLOR).pack(pady=(8, 4), anchor="w", padx=12)
        ent_class = tk.Entry(popup)
        ent_class.pack(fill="x", padx=12)

        tk.Label(popup, text="Roll (optional):", bg=BG_DARK, fg=TEXT_COLOR).pack(pady=(8, 4), anchor="w", padx=12)
        ent_roll = tk.Entry(popup)
        ent_roll.pack(fill="x", padx=12)

        def save_student():
            name = ent_name.get().strip()
            if not name:
                messagebox.showerror("Error", "Student name cannot be empty.", parent=popup)
                return
            if name in self.data["students"]:
                messagebox.showerror("Error", "A student with this name already exists.", parent=popup)
                return
            # create student structure
            self.data["students"][name] = {"info": {"class": ent_class.get().strip(), "roll": ent_roll.get().strip()},
                                          "subjects": {}}
            save_data(self.data)
            # refresh student menu
            vals = list(self.data["students"].keys())
            self.student_menu.configure(values=vals)
            self.student_var.set(name)
            self.current_student = name
            popup.destroy()
            self.selected_subject = None
            self.render_subject_cards()
            self.update_summary()

        tk.Button(popup, text="Add Student", bg=PEACH, fg="black", command=save_student).pack(pady=14)

    def delete_student(self):
        if not self.current_student:
            return
        students = list(self.data["students"].keys())
        if len(students) <= 1:
            messagebox.showwarning("Cannot Delete", "At least one student must remain.")
            return
        if messagebox.askyesno("Confirm Delete", f"Delete student '{self.current_student}' and all their data?"):
            del self.data["students"][self.current_student]
            save_data(self.data)
            # pick another student (first)
            remaining = list(self.data["students"].keys())
            self.current_student = remaining[0]
            self.student_menu.configure(values=remaining)
            self.student_var.set(self.current_student)
            self.selected_subject = None
            self.render_subject_cards()
            self.update_summary()

    # -------------------- SUBJECT CARD UI --------------------
    def clear_selection(self):
        self.selected_subject = None
        for s, frame in self.card_widgets.items():
            try:
                frame.configure(fg_color="#222325")
            except Exception:
                pass

    def select_subject(self, subject_name):
        # highlight the subject card
        self.clear_selection()
        self.selected_subject = subject_name
        widget = self.card_widgets.get(subject_name)
        if widget:
            widget.configure(fg_color="#2F4B3A")  # slightly different highlight

    def get_current_subjects(self):
        return self.data["students"][self.current_student]["subjects"]

    def render_subject_cards(self):
        # remove all current widgets inside scrollable frame
        for child in self.scrollable.winfo_children():
            child.destroy()
        self.card_widgets.clear()

        subjects = self.get_current_subjects()
        if not subjects:
            placeholder = ctk.CTkLabel(self.scrollable, text="No subjects yet — add a subject to begin!",
                                      font=("Segoe UI", 13), text_color="#BFC3C7")
            placeholder.pack(pady=20)
            return

        # create a card for each subject (sorted)
        for subj in sorted(subjects.keys(), key=str.lower):
            info = subjects[subj]
            attended = info.get("attended", 0)
            total = info.get("total", 0)
            perc = 100.0 if total == 0 else (attended / total) * 100.0

            # Calculate status
            goal = (self.goal_percent.get() / 100.0)
            if total == 0:
                status = "No classes held yet."
            else:
                if perc >= self.goal_percent.get():
                    try:
                        can_miss = int((attended / goal) - total)
                    except ZeroDivisionError:
                        can_miss = 0
                    can_miss = max(0, can_miss)
                    status = f"✅ Safe. You can miss {can_miss} class(es)."
                else:
                    import math
                    needed = max(0, math.ceil(((goal * total) - attended) / (1 - goal)))
                    status = f"⚠️ Danger! Attend next {needed} class(es)."

            card = ctk.CTkFrame(self.scrollable, fg_color="#222325", corner_radius=10, height=84)
            card.pack(fill="x", padx=10, pady=8)

            # clickable binding: select when clicked anywhere on the card
            def make_onclick(s=subj):
                return lambda e=None: self.select_subject(s)

            card.bind("<Button-1>", make_onclick())
            self.card_widgets[subj] = card

            # left: subject name + status
            left = ctk.CTkFrame(card, fg_color="#222325", corner_radius=0)
            left.pack(side="left", fill="both", expand=True, padx=(12, 6), pady=8)

            lbl_name = ctk.CTkLabel(left, text=subj, font=("Segoe UI", 14, "bold"), anchor="w")
            lbl_name.pack(fill="x")
            lbl_name.bind("<Button-1>", make_onclick())

            lbl_status = ctk.CTkLabel(left, text=status, font=("Segoe UI", 11), anchor="w")
            lbl_status.pack(fill="x", pady=(6, 0))
            lbl_status.bind("<Button-1>", make_onclick())

            # right: stats and quick buttons
            right = ctk.CTkFrame(card, fg_color="#222325", corner_radius=0)
            right.pack(side="right", padx=12, pady=8)

            lbl_stats = ctk.CTkLabel(right, text=f"{attended} / {total}\n{perc:.2f}%", font=("Segoe UI", 12, "bold"))
            lbl_stats.pack()

            # quick action small buttons
            btn_frame = ctk.CTkFrame(right, fg_color="#222325", corner_radius=0)
            btn_frame.pack(pady=(6, 0))
            ctk.CTkButton(btn_frame, text="✓", width=38, height=30, fg_color="#A3BE8C",
                          command=lambda s=subj: self._quick_attend(s)).pack(side="left", padx=4)
            ctk.CTkButton(btn_frame, text="✗", width=38, height=30, fg_color="#BF616A",
                          command=lambda s=subj: self._quick_miss(s)).pack(side="left", padx=4)

    # -------------------- Data Actions --------------------
    def add_subject(self):
        name = self.entry_subject.get().strip()
        if not name:
            messagebox.showerror("Error", "Subject name cannot be empty.")
            return
        subjects = self.get_current_subjects()
        if name in subjects:
            messagebox.showinfo("Exists", "Subject already exists for this student.")
            return
        subjects[name] = {"attended": 0, "total": 0}
        save_data(self.data)
        self.entry_subject.delete(0, tk.END)
        self.render_subject_cards()
        self.update_summary()

    def delete_subject(self):
        if not self.selected_subject:
            messagebox.showwarning("Select", "Please select a subject to delete (click a card).")
            return
        subjects = self.get_current_subjects()
        if messagebox.askyesno("Confirm Delete", f"Delete '{self.selected_subject}' for student '{self.current_student}'?"):
            del subjects[self.selected_subject]
            save_data(self.data)
            self.selected_subject = None
            self.render_subject_cards()
            self.update_summary()

    def mark_attended(self):
        if not self.selected_subject:
            messagebox.showwarning("Select", "Please select a subject (click a card) first.")
            return
        subjects = self.get_current_subjects()
        s = self.selected_subject
        subjects[s]["attended"] = subjects[s].get("attended", 0) + 1
        subjects[s]["total"] = subjects[s].get("total", 0) + 1
        save_data(self.data)
        self.render_subject_cards()
        self.update_summary()

    def mark_missed(self):
        if not self.selected_subject:
            messagebox.showwarning("Select", "Please select a subject (click a card) first.")
            return
        subjects = self.get_current_subjects()
        s = self.selected_subject
        subjects[s]["total"] = subjects[s].get("total", 0) + 1
        save_data(self.data)
        self.render_subject_cards()
        self.update_summary()

    def open_edit_window(self):
        if not self.selected_subject:
            messagebox.showwarning("Select", "Please select a subject to edit.")
            return
        subj = self.selected_subject
        subjects = self.get_current_subjects()
        info = subjects[subj]

        edit = tk.Toplevel(self.root)
        edit.title(f"Edit — {subj}")
        edit.geometry("360x220")
        edit.configure(bg=BG_DARK)

        tk.Label(edit, text=f"Editing: {subj}", font=("Segoe UI", 13, "bold"), bg=BG_DARK, fg=TEXT_COLOR).pack(pady=(12, 6))

        frm = tk.Frame(edit, bg=BG_DARK)
        frm.pack(pady=6)

        tk.Label(frm, text="Attended:", bg=BG_DARK, fg=TEXT_COLOR).grid(row=0, column=0, padx=8, pady=6, sticky="e")
        e_att = tk.Entry(frm)
        e_att.grid(row=0, column=1, padx=8, pady=6)
        e_att.insert(0, str(info.get("attended", 0)))

        tk.Label(frm, text="Total:", bg=BG_DARK, fg=TEXT_COLOR).grid(row=1, column=0, padx=8, pady=6, sticky="e")
        e_tot = tk.Entry(frm)
        e_tot.grid(row=1, column=1, padx=8, pady=6)
        e_tot.insert(0, str(info.get("total", 0)))

        def save_edit():
            try:
                a = int(e_att.get())
                t = int(e_tot.get())
                if a < 0 or t < 0 or a > t:
                    messagebox.showerror("Invalid", "Please enter logical numbers (0 <= attended <= total).", parent=edit)
                    return
                subjects[subj]["attended"] = a
                subjects[subj]["total"] = t
                save_data(self.data)
                edit.destroy()
                self.render_subject_cards()
                self.update_summary()
            except ValueError:
                messagebox.showerror("Invalid", "Please enter valid integers.", parent=edit)

        tk.Button(edit, text="Save", bg=PEACH, fg="black", command=save_edit).pack(pady=10)

    # quick per-card actions used by the small ✓ / ✗ buttons
    def _quick_attend(self, subj):
        subjects = self.get_current_subjects()
        subjects[subj]["attended"] = subjects[subj].get("attended", 0) + 1
        subjects[subj]["total"] = subjects[subj].get("total", 0) + 1
        save_data(self.data)
        self.render_subject_cards()
        self.update_summary()

    def _quick_miss(self, subj):
        subjects = self.get_current_subjects()
        subjects[subj]["total"] = subjects[subj].get("total", 0) + 1
        save_data(self.data)
        self.render_subject_cards()
        self.update_summary()

    # -------------------- Settings --------------------
    def set_goal(self):
        new_goal = simpledialog.askfloat("Set Attendance Goal", "Enter new attendance goal (%)",
                                         parent=self.root, minvalue=1.0, maxvalue=100.0,
                                         initialvalue=self.goal_percent.get())
        if new_goal is not None:
            self.goal_percent.set(new_goal)
            self.data["settings"]["goal"] = new_goal
            save_data(self.data)
            self.goal_label.configure(text=f"Goal: {self.goal_percent.get():.0f}%")
            self.render_subject_cards()
            self.update_summary()

    def reset_all_data(self):
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to delete ALL students and their data? This cannot be undone."):
            self.data = {"students": {"Default Student": {"info": {}, "subjects": {}}}, "settings": {"goal": 75.0}}
            save_data(self.data)
            # refresh student menu
            vals = list(self.data["students"].keys())
            self.student_menu.configure(values=vals)
            self.student_var.set("Default Student")
            self.current_student = "Default Student"
            self.selected_subject = None
            self.render_subject_cards()
            self.update_summary()

    # -------------------- Summary --------------------
    def update_summary(self):
        subjects = self.get_current_subjects()
        total_sub = len(subjects)
        overall_att = 0
        overall_total = 0
        danger_count = 0

        goal = (self.goal_percent.get() / 100.0)
        for subj, info in subjects.items():
            a = info.get("attended", 0)
            t = info.get("total", 0)
            overall_att += a
            overall_total += t
            perc = 100.0 if t == 0 else (a / t) * 100.0
            if t != 0 and perc < self.goal_percent.get():
                danger_count += 1

        overall_perc = 100.0 if overall_total == 0 else (overall_att / overall_total) * 100.0
        st_info = self.data["students"][self.current_student].get("info", {})
        info_str = ""
        if st_info.get("class"):
            info_str += f" Class: {st_info.get('class')}"
        if st_info.get("roll"):
            info_str += f"  Roll: {st_info.get('roll')}"
        txt = f"Student: {self.current_student}{info_str}    Subjects: {total_sub}    Overall: {overall_att}/{overall_total} ({overall_perc:.2f}%)    At-risk: {danger_count}"
        self.summary_label.configure(text=txt)


# ---------------- Run Application ----------------
if __name__ == "__main__":
    root = ctk.CTk()
    app = AttendanceApp(root)
    root.mainloop()