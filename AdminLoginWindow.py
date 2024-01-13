import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess
import sqlite3

class AdminLoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Login")
        self.root.geometry("300x150")

        # Username and password variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        # Username label and entry
        self.username_label = tk.Label(root, text="Username:")
        self.username_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.username_entry = tk.Entry(root, textvariable=self.username_var)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5, sticky='e')

        # Password label and entry
        self.password_label = tk.Label(root, text="Password:")
        self.password_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.password_entry = tk.Entry(root, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5, sticky='e')

        # Load icons for login and exit buttons
        self.login_img = Image.open("user.png")  # Replace with the path to your login icon
        self.login_img = self.login_img.resize((20, 20), Image.ANTIALIAS)
        self.login_img = ImageTk.PhotoImage(self.login_img)

        self.exit_img = Image.open("exit.png")  # Replace with the path to your exit icon
        self.exit_img = self.exit_img.resize((20, 20), Image.ANTIALIAS)
        self.exit_img = ImageTk.PhotoImage(self.exit_img)

        # Frame to hold buttons
        self.button_frame = tk.Frame(root)
        self.button_frame.grid(row=2, column=0, columnspan=2)

        # Login button with icon
        self.login_button = tk.Button(root, text="Login", image=self.login_img, compound="left", command=self.login)
        self.login_button.grid(row=2, column=0, padx=10, pady=5)

        # Exit button with icon
        self.exit_button = tk.Button(root, text="Exit", image=self.exit_img, compound="left", command=self.exit_program)
        self.exit_button.grid(row=2, column=1, padx=10, pady=5)

        # Connect to the SQLite database
        self.conn = sqlite3.connect('chatbot_database.db')
        self.cursor = self.conn.cursor()

    def login(self):
        # Fetch username and password from the database and check if they match
        username = self.username_var.get()
        password = self.password_var.get()

        # Replace 'admins' with the name of the table in your database
        self.cursor.execute('SELECT * FROM admins WHERE username = ? AND password = ?', (username, password))
        admin = self.cursor.fetchone()
        if admin:
            print("Admin login successful!")
            messagebox.showinfo("Success", "You have successfully logged in as an admin.")
            # Close the login window
            self.root.destroy()
            # Open the report.py using subprocess
            subprocess.Popen(["python", "report.py"])
        else:
            print("Invalid username or password. Please try again.")
            messagebox.showerror("Error", "Invalid username or password. Please try again.")
    def exit_program(self):
        # Close the database connection and exit
        self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    admin_login = AdminLoginWindow(root)
    root.mainloop()
