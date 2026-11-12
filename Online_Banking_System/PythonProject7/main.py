
import hashlib
import hmac
import os
import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal, InvalidOperation
import mysql.connector
from mysql.connector import Error


# MYSQL DATABASE CONNECTION
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "12345678",
    "database": "online_banking_db",
    "port": 3306
}

PBKDF2_ITERATIONS = 300_000


# CONNECT TO MYSQL
def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


# CREATE DATABASE TABLES
def initialize_database():
    conn = connect_db()
    cur = conn.cursor()

    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password_salt BINARY(16) NOT NULL,
                password_hash BINARY(32) NOT NULL,
                balance_cents BIGINT NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK (balance_cents >= 0)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INT AUTO_INCREMENT PRIMARY KEY,
                account_id INT NOT NULL,
                transaction_type ENUM('DEPOSIT','WITHDRAWAL') NOT NULL,
                amount_cents BIGINT NOT NULL,
                balance_after_cents BIGINT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK (amount_cents > 0),
                CHECK (balance_after_cents >= 0),
                FOREIGN KEY (account_id)
                    REFERENCES accounts(account_id)
                    ON DELETE CASCADE
            )
        """)

        conn.commit()

    except Error:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()


# PASSWORD HASHING
def make_password_hash(password, salt=None):
    if salt is None:
        salt = os.urandom(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS
    )

    return salt, hashed


# VALIDATE MONEY
def amount_to_paise(value):
    value = value.strip().replace(",", "")

    if not value:
        raise ValueError("Please enter an amount.")

    try:
        amount = Decimal(value)
    except InvalidOperation:
        raise ValueError("Enter a valid amount.")

    if not amount.is_finite() or amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    if amount.as_tuple().exponent < -2:
        raise ValueError("Use no more than two decimal places.")

    return int(amount * 100)


# DISPLAY MONEY
def show_money(paise):
    return f"₹{paise / 100:,.2f}"


# MAIN BANKING APPLICATION
class BankingApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Online Banking System")
        self.root.geometry("720x540")
        self.root.minsize(620, 480)

        self.account = None

        self.welcome_screen()

    # CLEAR SCREEN
    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # WELCOME SCREEN
    def welcome_screen(self):
        self.account = None
        self.clear()

        frame = ttk.Frame(self.root, padding=30)
        frame.pack(expand=True)

        ttk.Label(
            frame,
            text="ONLINE BANKING SYSTEM",
            font=("Arial", 20, "bold")
        ).pack(pady=25)

        ttk.Label(
            frame,
            text="Python + Tkinter + MySQL"
        ).pack(pady=8)

        ttk.Button(
            frame,
            text="Create Account",
            command=self.register_screen
        ).pack(pady=10, ipadx=15, ipady=6)

        ttk.Button(
            frame,
            text="Login",
            command=self.login_screen
        ).pack(pady=10, ipadx=35, ipady=6)

        ttk.Label(
            frame,
            text="Educational demo only; not a real bank.",
            foreground="gray"
        ).pack(pady=25)

    # REGISTRATION SCREEN
    def register_screen(self):
        self.clear()

        frame = ttk.Frame(self.root, padding=30)
        frame.pack(expand=True)

        ttk.Label(
            frame,
            text="Create Account",
            font=("Arial", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=15)

        ttk.Label(frame, text="Username").grid(
            row=1, column=0, padx=8, pady=8
        )

        username = ttk.Entry(frame, width=30)
        username.grid(row=1, column=1, pady=8)

        ttk.Label(frame, text="Password").grid(
            row=2, column=0, padx=8, pady=8
        )

        password = ttk.Entry(frame, width=30, show="*")
        password.grid(row=2, column=1, pady=8)

        ttk.Label(frame, text="Confirm password").grid(
            row=3, column=0, padx=8, pady=8
        )

        confirm = ttk.Entry(frame, width=30, show="*")
        confirm.grid(row=3, column=1, pady=8)

        def register():

            name = username.get().strip()
            pwd = password.get()

            if not name or not pwd or not confirm.get():
                messagebox.showerror(
                    "Error", "Please fill in all fields."
                )
                return

            if len(name) < 3 or len(name) > 50:
                messagebox.showerror(
                    "Error", "Username must be 3 to 50 characters."
                )
                return

            if len(pwd) < 8:
                messagebox.showerror(
                    "Error", "Password must be at least 8 characters."
                )
                return

            if pwd != confirm.get():
                messagebox.showerror(
                    "Error", "Passwords do not match."
                )
                return

            salt, password_hash = make_password_hash(pwd)

            conn = cur = None

            try:
                conn = connect_db()
                cur = conn.cursor()

                cur.execute(
                    """
                    INSERT INTO accounts
                    (username, password_salt,
                     password_hash, balance_cents)
                    VALUES (%s, %s, %s, 0)
                    """,
                    (name, salt, password_hash)
                )

                conn.commit()

                messagebox.showinfo(
                    "Success",
                    "Account created. Please log in."
                )

                self.login_screen()

            except mysql.connector.IntegrityError:
                if conn:
                    conn.rollback()

                messagebox.showerror(
                    "Error",
                    "That username already exists."
                )

            except Error as error:
                if conn:
                    conn.rollback()

                messagebox.showerror(
                    "Database error", str(error)
                )

            finally:
                if cur:
                    cur.close()

                if conn and conn.is_connected():
                    conn.close()

        ttk.Button(
            frame,
            text="Create Account",
            command=register
        ).grid(row=4, column=0, columnspan=2, pady=15)

        ttk.Button(
            frame,
            text="Back",
            command=self.welcome_screen
        ).grid(row=5, column=0, columnspan=2)

    # LOGIN SCREEN
    def login_screen(self):
        self.clear()

        frame = ttk.Frame(self.root, padding=30)
        frame.pack(expand=True)

        ttk.Label(
            frame,
            text="Login",
            font=("Arial", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=15)

        ttk.Label(frame, text="Username").grid(
            row=1, column=0, padx=8, pady=8
        )

        username = ttk.Entry(frame, width=30)
        username.grid(row=1, column=1, pady=8)

        ttk.Label(frame, text="Password").grid(
            row=2, column=0, padx=8, pady=8
        )

        password = ttk.Entry(frame, width=30, show="*")
        password.grid(row=2, column=1, pady=8)

        def login():

            name = username.get().strip()
            pwd = password.get()

            if not name or not pwd:
                messagebox.showerror(
                    "Error", "Enter username and password."
                )
                return

            conn = cur = None

            try:
                conn = connect_db()
                cur = conn.cursor()

                cur.execute(
                    """
                    SELECT account_id, username,
                           password_salt, password_hash
                    FROM accounts
                    WHERE username = %s
                    """,
                    (name,)
                )

                row = cur.fetchone()

            except Error as error:
                messagebox.showerror(
                    "Database error", str(error)
                )
                return

            finally:
                if cur:
                    cur.close()

                if conn and conn.is_connected():
                    conn.close()

            if not row:
                messagebox.showerror(
                    "Login failed",
                    "Incorrect username or password."
                )
                return

            account_id, saved_name, salt, saved_hash = row

            _, entered_hash = make_password_hash(pwd, salt)

            if not hmac.compare_digest(
                entered_hash, saved_hash
            ):
                messagebox.showerror(
                    "Login failed",
                    "Incorrect username or password."
                )
                return

            self.account = (account_id, saved_name)

            self.dashboard()

        ttk.Button(
            frame,
            text="Login",
            command=login
        ).grid(row=3, column=0, columnspan=2, pady=15)

        ttk.Button(
            frame,
            text="Back",
            command=self.welcome_screen
        ).grid(row=4, column=0, columnspan=2)

    # GET ACCOUNT BALANCE
    def get_balance(self):

        conn = connect_db()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                SELECT balance_cents
                FROM accounts
                WHERE account_id = %s
                """,
                (self.account[0],)
            )

            row = cur.fetchone()

            if row is None:
                raise RuntimeError("Account not found.")

            return row[0]

        finally:
            cur.close()
            conn.close()

    # DASHBOARD
    def dashboard(self):
        self.clear()

        top = ttk.Frame(self.root, padding=18)
        top.pack(fill="x")

        ttk.Label(
            top,
            text=f"Welcome, {self.account[1]}!",
            font=("Arial", 18, "bold")
        ).pack(side="left")

        ttk.Button(
            top,
            text="Logout",
            command=self.welcome_screen
        ).pack(side="right")

        self.balance_label = ttk.Label(
            self.root,
            text="",
            font=("Arial", 17, "bold"),
            foreground="green"
        )

        self.balance_label.pack(pady=15)

        self.refresh_balance()

        actions = ttk.LabelFrame(
            self.root,
            text="Banking Actions",
            padding=15
        )

        actions.pack(fill="x", padx=20, pady=10)

        ttk.Label(actions, text="Amount (₹)").grid(
            row=0, column=0, padx=5, pady=8
        )

        self.amount_entry = ttk.Entry(actions, width=20)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=8)

        ttk.Button(
            actions,
            text="Deposit",
            command=self.deposit
        ).grid(row=0, column=2, padx=5)

        ttk.Button(
            actions,
            text="Withdraw",
            command=self.withdraw
        ).grid(row=0, column=3, padx=5)

        ttk.Button(
            actions,
            text="Refresh Balance",
            command=self.refresh_balance
        ).grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Button(
            actions,
            text="Transaction History",
            command=self.history
        ).grid(row=1, column=2, columnspan=2, pady=10)

        ttk.Label(
            self.root,
            text="Demo only: no real money or bank connection.",
            foreground="gray"
        ).pack(pady=10)

    # REFRESH BALANCE
    def refresh_balance(self):

        try:
            self.balance_label.config(
                text=f"Available Balance: {show_money(self.get_balance())}"
            )

        except (Error, RuntimeError) as error:
            messagebox.showerror("Error", str(error))

    # DEPOSIT AND WITHDRAW DATABASE OPERATION
    def perform_transaction(self, kind, amount):

        conn = connect_db()
        cur = conn.cursor()

        try:
            conn.start_transaction()

            cur.execute(
                """
                SELECT balance_cents
                FROM accounts
                WHERE account_id = %s
                FOR UPDATE
                """,
                (self.account[0],)
            )

            row = cur.fetchone()

            if row is None:
                raise RuntimeError("Account not found.")

            old_balance = row[0]

            if kind == "WITHDRAWAL" and amount > old_balance:
                raise ValueError(
                    f"Insufficient funds. Current balance: {show_money(old_balance)}"
                )

            if kind == "DEPOSIT":
                new_balance = old_balance + amount
            else:
                new_balance = old_balance - amount

            cur.execute(
                """
                UPDATE accounts
                SET balance_cents = %s
                WHERE account_id = %s
                """,
                (new_balance, self.account[0])
            )

            cur.execute(
                """
                INSERT INTO transactions
                (account_id, transaction_type,
                 amount_cents, balance_after_cents)
                VALUES (%s, %s, %s, %s)
                """,
                (self.account[0], kind, amount, new_balance)
            )

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            cur.close()
            conn.close()

    # DEPOSIT
    def deposit(self):

        try:
            amount = amount_to_paise(
                self.amount_entry.get()
            )

            self.perform_transaction("DEPOSIT", amount)

            self.amount_entry.delete(0, tk.END)

            self.refresh_balance()

            messagebox.showinfo(
                "Success",
                f"Deposited {show_money(amount)}."
            )

        except ValueError as error:
            messagebox.showerror("Deposit error", str(error))

        except (Error, RuntimeError) as error:
            messagebox.showerror("Transaction error", str(error))

    # WITHDRAW
    def withdraw(self):

        try:
            amount = amount_to_paise(
                self.amount_entry.get()
            )

            self.perform_transaction("WITHDRAWAL", amount)

            self.amount_entry.delete(0, tk.END)

            self.refresh_balance()

            messagebox.showinfo(
                "Success",
                f"Withdrew {show_money(amount)}."
            )

        except ValueError as error:
            messagebox.showerror("Withdrawal error", str(error))

        except (Error, RuntimeError) as error:
            messagebox.showerror("Transaction error", str(error))

    # TRANSACTION HISTORY
    def history(self):

        window = tk.Toplevel(self.root)
        window.title("Transaction History")
        window.geometry("700x350")

        columns = (
            "date",
            "type",
            "amount",
            "balance"
        )

        table = ttk.Treeview(
            window,
            columns=columns,
            show="headings"
        )

        for col, heading in [
            ("date", "Date and Time"),
            ("type", "Transaction"),
            ("amount", "Amount"),
            ("balance", "Balance After")
        ]:
            table.heading(col, text=heading)

        table.column("date", width=190)
        table.column("type", width=120)
        table.column("amount", width=130, anchor="e")
        table.column("balance", width=140, anchor="e")

        scroll = ttk.Scrollbar(
            window,
            orient="vertical",
            command=table.yview
        )

        table.configure(yscrollcommand=scroll.set)

        table.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(10, 0),
            pady=10
        )

        scroll.pack(
            side="right",
            fill="y",
            padx=(0, 10),
            pady=10
        )

        conn = cur = None

        try:
            conn = connect_db()
            cur = conn.cursor()

            cur.execute(
                """
                SELECT created_at,
                       transaction_type,
                       amount_cents,
                       balance_after_cents
                FROM transactions
                WHERE account_id = %s
                ORDER BY transaction_id DESC
                """,
                (self.account[0],)
            )

            rows = cur.fetchall()

            if not rows:
                table.insert(
                    "",
                    "end",
                    values=("No transactions yet", "-", "-", "-")
                )

            for date, kind, amount, balance in rows:
                table.insert(
                    "",
                    "end",
                    values=(
                        date,
                        kind.title(),
                        show_money(amount),
                        show_money(balance)
                    )
                )

        except Error as error:
            window.destroy()
            messagebox.showerror(
                "Database error", str(error)
            )

        finally:
            if cur:
                cur.close()

            if conn and conn.is_connected():
                conn.close()


# MAIN FUNCTION
def main():

    try:
        initialize_database()

        root = tk.Tk()

        BankingApp(root)

        root.mainloop()

    except Error as error:
        messagebox.showerror(
            "MySQL Connection Error",
            "Check that MySQL Server is running, "
            "the database exists, and DB_CONFIG "
            "has the correct username/password.\n\n"
            f"Details: {error}"
        )


if __name__ == "__main__":
    main()
