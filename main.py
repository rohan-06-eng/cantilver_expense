import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt


# Database setup
def init_db():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category_id INTEGER,
            amount REAL,
            date TEXT,
            description TEXT,
            FOREIGN KEY(user_id) REFERENCES Users(id),
            FOREIGN KEY(category_id) REFERENCES Categories(id)
        )
    ''')
    conn.commit()

    # Predefined categories
    categories = ['Food', 'Transportation', 'Utilities', 'Entertainment', 'Healthcare', 'Education', 'Miscellaneous']
    cursor.executemany("INSERT OR IGNORE INTO Categories (name) VALUES (?)", [(category,) for category in categories])
    conn.commit()
    conn.close()


# Gradient background function
def create_gradient(canvas, color1, color2):
    width = canvas.winfo_reqwidth()
    height = canvas.winfo_reqheight()
    gradient = tk.PhotoImage(width=width, height=height)
    for i in range(height):
        r = int(color1[0] + (color2[0] - color1[0]) * i / height)
        g = int(color1[1] + (color2[1] - color1[1]) * i / height)
        b = int(color1[2] + (color2[2] - color1[2]) * i / height)
        gradient.put(f'#{r:02x}{g:02x}{b:02x}', (0, i, width, i + 1))
    canvas.create_image((0, 0), image=gradient, anchor='nw')
    canvas.image = gradient


# GUI Components
class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x600")  # Larger window size for better visibility

        # Gradient background
        self.canvas = tk.Canvas(root, width=800, height=600, bg='#ffffff', highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        create_gradient(self.canvas, (0, 150, 136), (255, 255, 255))  # Teal to white gradient

        # Create a frame to hold the widgets
        self.frame = tk.Frame(self.canvas, bg='#ffffff', padx=20, pady=20)
        self.frame.place(relx=0.5, rely=0.5, anchor='center')

        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12, "bold"), padding=10)
        self.style.configure("TEntry", font=("Arial", 12), padding=5)
        self.style.configure("TLabel", font=("Arial", 12))

        # Define custom button styles
        self.style.configure("Login.TButton", background="#00bcd4", foreground="black", padding=(10, 5))
        self.style.map("Login.TButton", background=[("active", "#0097a7")], foreground=[("pressed", "black")])
        self.style.configure("Register.TButton", background="#4caf50", foreground="black", padding=(10, 5))
        self.style.map("Register.TButton", background=[("active", "#388e3c")], foreground=[("pressed", "black")])
        self.style.configure("Add.TButton", background="#00bcd4", foreground="black", padding=(10, 5))
        self.style.map("Add.TButton", background=[("active", "#0097a7")], foreground=[("pressed", "black")])
        self.style.configure("Report.TButton", background="#ff9800", foreground="black", padding=(10, 5))
        self.style.map("Report.TButton", background=[("active", "#fb8c00")], foreground=[("pressed", "black")])

        # Center the window
        self.center_window()

        # Initialize frames
        self.auth_frame = ttk.Frame(self.frame, padding=20, style="TFrame")
        self.auth_frame.grid(row=0, column=0, padx=20, pady=20)

        self.create_login_widgets()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_login_widgets(self):
        self.clear_frame(self.auth_frame)

        # Username
        ttk.Label(self.auth_frame, text="Username:").grid(row=0, column=0, sticky="e", padx=10, pady=10)
        self.username_entry = tk.Entry(self.auth_frame, font=("Arial", 12), bd=2, relief="solid", bg="#e0f2f1",
                                       fg="black")
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        # Password
        ttk.Label(self.auth_frame, text="Password:").grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.password_entry = tk.Entry(self.auth_frame, show="*", font=("Arial", 12), bd=2, relief="solid",
                                       bg="#e0f2f1", fg="black")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        # Login and Register Buttons
        login_button = ttk.Button(self.auth_frame, text="Login", command=self.login, style="Login.TButton")
        login_button.grid(row=2, column=0, pady=20, columnspan=2)

        register_button = ttk.Button(self.auth_frame, text="Register", command=self.register, style="Register.TButton")
        register_button.grid(row=3, column=0, pady=10, columnspan=2)

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM Users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        if user:
            self.user_id = user[0]
            self.main_screen()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

        conn.close()

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO Users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Registration Successful", "You can now log in")
        except sqlite3.IntegrityError:
            messagebox.showerror("Registration Failed", "Username already exists")

        conn.close()

    def main_screen(self):
        self.clear_frame(self.auth_frame)

        # Expense Entry Frame
        self.expense_frame = ttk.Frame(self.frame, padding=20, style="TFrame")
        self.expense_frame.grid(row=0, column=0, padx=20, pady=20)

        ttk.Label(self.expense_frame, text="Amount:").grid(row=0, column=0, sticky="e", padx=10, pady=10)
        self.amount_entry = tk.Entry(self.expense_frame, font=("Arial", 12), bd=2, relief="solid", bg="#e0f2f1",
                                     fg="black")
        self.amount_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self.expense_frame, text="Category:").grid(row=1, column=0, sticky="e", padx=10, pady=10)

        # Dropdown for predefined categories
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(self.expense_frame, textvariable=self.category_var, state="readonly",
                                              font=("Arial", 12))
        self.load_categories()
        self.category_dropdown.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self.expense_frame, text="Description:").grid(row=2, column=0, sticky="e", padx=10, pady=10)
        self.description_entry = tk.Entry(self.expense_frame, font=("Arial", 12), bd=2, relief="solid", bg="#e0f2f1",
                                          fg="black")
        self.description_entry.grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(self.expense_frame, text="Date:").grid(row=3, column=0, sticky="e", padx=10, pady=10)
        self.date_entry = tk.Entry(self.expense_frame, font=("Arial", 12), bd=2, relief="solid", bg="#e0f2f1",
                                   fg="black")
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.date_entry.grid(row=3, column=1, padx=10, pady=10)

        add_button = ttk.Button(self.expense_frame, text="Add Expense", command=self.add_expense, style="Add.TButton")
        add_button.grid(row=4, column=0, pady=20, columnspan=2)

        report_button = ttk.Button(self.expense_frame, text="Generate Report", command=self.generate_report,
                                   style="Report.TButton")
        report_button.grid(row=5, column=0, pady=10, columnspan=2)

    def load_categories(self):
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Categories")
        categories = [row[0] for row in cursor.fetchall()]
        self.category_dropdown['values'] = categories
        conn.close()

    def add_expense(self):
        amount = self.amount_entry.get()
        category = self.category_var.get()
        description = self.description_entry.get()
        date = self.date_entry.get()

        if not amount or not category:
            messagebox.showwarning("Input Error", "Amount and Category are required")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showwarning("Input Error", "Amount must be a number")
            return

        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM Categories WHERE name=?", (category,))
        category_id = cursor.fetchone()[0]

        cursor.execute("INSERT INTO Expenses (user_id, category_id, amount, date, description) VALUES (?, ?, ?, ?, ?)",
                       (self.user_id, category_id, amount, date, description))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Expense added successfully")

    def generate_report(self):
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT Categories.name, SUM(Expenses.amount) 
            FROM Expenses
            JOIN Categories ON Expenses.category_id = Categories.id
            WHERE Expenses.user_id = ?
            GROUP BY Categories.name
        ''', (self.user_id,))
        data = cursor.fetchall()
        conn.close()

        if not data:
            messagebox.showinfo("No Data", "No expenses found for generating report")
            return

        categories, amounts = zip(*data)

        plt.figure(figsize=(10, 7))
        plt.bar(categories, amounts, color='teal')
        plt.xlabel('Category')
        plt.ylabel('Amount')
        plt.title('Expense Report')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
