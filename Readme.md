# Pro Attendance Tracker 📊

A modern, easy-to-use desktop application built with Python to help students track their class attendance and stay above their academic goals. Never guess your attendance percentage again!



---

## ✨ Features

* **Add, Edit, & Delete Subjects:** Easily manage your list of courses for the semester.
* **Track Attendance:** Mark classes as "Attended" or "Missed" with a single click.
* **Smart Status Calculation:** Instantly know your status for each subject:
    * ✅ **Safe:** Calculates exactly how many classes you can afford to miss.
    * ⚠️ **Danger:** Calculates how many classes you *must* attend to reach your goal.
* **Customizable Goal:** Set your own attendance target (e.g., 75%, 80%) via the File menu.
* **Modern Interface:** A clean, themed user interface built with Tkinter's `ttk` widgets.
* **Persistent Data:** Your attendance data is automatically saved to a `json` file and reloaded every time you open the app.

---

## 🛠️ Technology Stack

* **Language:** **Python 3**
* **GUI Library:** **Tkinter** (specifically the `ttk` themed widgets for a modern look)
* **Data Storage:** **JSON** for simple, human-readable data persistence.

---

## 🚀 Getting Started

This project uses only Python's built-in libraries, so no special installation is required.

### Prerequisites

* **Python 3.6** or newer installed on your system.

### Installation & Usage

1.  **Clone the repository or download the source code.**
    If you have Git installed:
    ```bash
    git clone <your-repository-link>
    cd <repository-folder>
    ```
    Otherwise, just download the `pro_tracker.py` file.

2.  **Run the application.**
    Open your terminal or command prompt, navigate to the project directory, and run the following command:
    ```bash
    python pro_tracker.py
    ```
    The application window should now appear!

---

## 📂 File Structure

The project consists of two main files:

* pro_tracker.py              # The main Python script containing all the application logic and GUI.
* attendance_pro_data.json    # The data file that is automatically created to store your subjects and settings.

---

## 💡 How It Works

The application is built as a single class `AttendanceApp` that handles both the GUI and the logic.

* **GUI:** The user interface is constructed using widgets from Python's `tkinter.ttk` library. Buttons and menu items are linked to callback functions that trigger the application's logic.
* **Data Handling:** All subject data (attended/total classes) and user settings (attendance goal) are stored in a Python dictionary. This dictionary is saved to `attendance_pro_data.json` whenever a change is made, ensuring no data is lost between sessions. When the app starts, it reads this file to restore the previous state.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to fork the repo and submit a pull request.

---

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for details.


