import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog
from PIL import Image, ImageTk
import sqlite3
from openpyxl import Workbook
from ttkthemes import ThemedTk

class Report:
    def __init__(self, root):
        self.root = root
        self.root.set_theme("plastik")
        self.root.title("Report")
        self.root.geometry("400x150")

        # Define username and password variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root)
        frame.grid(row=0, column=0, padx=10, pady=10)

        # Load icons for buttons
        load_json_img = Image.open("file.png")
        load_json_img = load_json_img.resize((30, 30), Image.ANTIALIAS)
        load_json_img = ImageTk.PhotoImage(load_json_img)

        create_report_img = Image.open("report.png")
        create_report_img = create_report_img.resize((30, 30), Image.ANTIALIAS)
        create_report_img = ImageTk.PhotoImage(create_report_img)

        username_label = ttk.Label(frame, text="Username:")
        username_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        username_entry = ttk.Entry(frame, textvariable=self.username_var)
        username_entry.grid(row=0, column=1, padx=10, pady=5, sticky='e')

        password_label = ttk.Label(frame, text="Password:")
        password_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')
        password_entry = ttk.Entry(frame, textvariable=self.password_var, show="*")
        password_entry.grid(row=1, column=1, padx=10, pady=5, sticky='e')

        load_json_button = ttk.Button(frame, text="Load JSON", image=load_json_img, compound="left", command=self.load_json)
        load_json_button.grid(row=0, column=2, padx=10, pady=5)

        create_report_button = ttk.Button(frame, text="Create Report", image=create_report_img, compound="left", command=self.create_report)
        create_report_button.grid(row=1, column=2, padx=10, pady=5)

        add_admin_button = ttk.Button(frame, text="Add Admin", command=self.add_admin)
        add_admin_button.grid(row=2, column=0, padx=10, pady=5)

        delete_user_button = ttk.Button(frame, text="Delete User", command=self.delete_user)
        delete_user_button.grid(row=2, column=1, padx=10, pady=5)

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.center_widgets()

    def center_widgets(self):
        window_width = self.root.winfo_reqwidth()
        window_height = self.root.winfo_reqheight()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))

        self.root.geometry("+{}+{}".format(x, y))

        self.conn = sqlite3.connect('chatbot_database.db')
        self.cursor = self.conn.cursor()

    def load_json(self):
        file_path = 'English.json'

        try:
            subprocess.Popen(["notepad", file_path])
        except Exception as e:
            messagebox.showerror("Error", f"Error opening English.json: {e}")

    def add_admin(self):
        username = self.username_var.get()
        password = self.password_var.get()
        if username and password:
            try:
                self.cursor.execute('INSERT INTO admins (username, password) VALUES (?, ?)', (username, password))
                self.conn.commit()
                messagebox.showinfo("Success", "Admin added successfully.")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Admin with this username already exists.")
        else:
            messagebox.showerror("Error", "Please provide both username and password.")

    def delete_user(self):
        username_to_delete = self.username_var.get()
        if username_to_delete:
            try:
                self.cursor.execute('DELETE FROM admins WHERE username = ?', (username_to_delete,))
                if self.cursor.rowcount > 0:
                    self.conn.commit()
                    messagebox.showinfo("Success", f"Admin '{username_to_delete}' deleted successfully.")
                else:
                    messagebox.showerror("Error", f"Admin '{username_to_delete}' not found.")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        else:
            messagebox.showerror("Error", "Please provide the username to delete.")

    def create_report(self):
        month = simpledialog.askinteger("Input", "Enter the month (e.g., 1 for January):", parent=self.root, minvalue=1, maxvalue=12)
        year = simpledialog.askinteger("Input", "Enter the year (e.g., 2023):", parent=self.root, minvalue=1900, maxvalue=3000)
        if month is not None and year is not None:
            chat_history = self.fetch_chat_history(month, year)
            if chat_history:
                workbook = Workbook()
                worksheet = workbook.active
                worksheet.append(["Input Message", "Output Message", "Timestamp"])
                for row in chat_history:
                    worksheet.append(row)
                report_filename = f"Chat_Report_{month}_{year}.xlsx"
                workbook.save(report_filename)
                messagebox.showinfo("Success", f"Report for {month}-{year} has been created and saved as '{report_filename}'.")
            else:
                messagebox.showerror("Error", "No chat history found for the specified month and year.")

    def fetch_chat_history(self, month, year):
        query = "SELECT input_message, output_message, timestamp FROM chat_history WHERE strftime('%m', timestamp) = ? AND strftime('%Y', timestamp) = ?"
        data = self.cursor.execute(query, (str(month).zfill(2), str(year)))
        chat_history = data.fetchall()
        return chat_history
if __name__ == "__main__":
    root = ThemedTk(theme="plastik")
    app = Report(root)
    root.mainloop()
