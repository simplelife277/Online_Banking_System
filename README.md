# 🏦 Online Banking System using Python and MySQL

## 📌 Project Overview

The **Online Banking System** is a desktop-based banking application developed using Python, Tkinter, and MySQL.

This project allows users to create bank accounts, log in securely, check their account balance, deposit money, withdraw money, and view transaction history through a simple graphical user interface (GUI).

The application uses MySQL to store account and transaction information.

## 🚀 Features

- **Account Registration** – Create a new bank account.
- **Secure Login** – Log in using account credentials.
- **Password Hashing** – Passwords are stored as secure hashes.
- **Balance Enquiry** – View the current account balance.
- **Deposit Money** – Add money to an account.
- **Withdraw Money** – Withdraw money from an account.
- **Transaction History** – View previous deposits and withdrawals.
- **MySQL Database** – Store account and transaction records.
- **User-Friendly GUI** – Simple interface built with Tkinter.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application development |
| Tkinter | Graphical User Interface |
| MySQL | Database management |
| MySQL Connector | Python–MySQL connection |
| hashlib | Password hashing |

## 📂 Project Structure

```text
Online_Banking_System/
│
├── main.py
├── database.sql
├── requirements.txt
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Open the Project Folder

```bash
cd Online_Banking_System
```

### 3. Install Required Package

```bash
pip install -r requirements.txt
```

### 4. Configure MySQL

1. Open MySQL Workbench.
2. Connect to your MySQL server.
3. Open and execute `database.sql`.
4. Open `main.py`.
5. Update the database configuration with your MySQL credentials.

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_MYSQL_PASSWORD",
    "database": "online_banking_db",
    "port": 3306
}
```

**Important:** Replace `YOUR_MYSQL_PASSWORD` with your own MySQL password. Never upload your real database password to GitHub.

### 5. Run the Application

```bash
python main.py
```

## 🗄️ Database Tables

### Accounts Table

Stores user account information.

- Account ID
- Account Holder Name
- Email
- Password Hash
- Account Balance

### Transactions Table

Stores banking transaction records.

- Transaction ID
- Account ID
- Transaction Type
- Transaction Amount
- Transaction Date

## 🔄 Application Workflow

```text
        START
          |
          v
    Welcome Screen
          |
     +----+----+
     |         |
  Register    Login
     |         |
     v         v
 Create      Verify
 Account   Credentials
               |
               v
        Banking Dashboard
               |
       +-------+-------+
       |       |       |
     Deposit Withdraw History
       |       |       |
       +-------+-------+
               |
               v
         MySQL Database
```

## 🎯 Learning Outcomes

Through this project, I practised:

- Python programming and functions.
- Object-Oriented Programming (OOP).
- Tkinter GUI development.
- MySQL database integration.
- SQL queries and database operations.
- Password hashing.
- Error handling and input validation.
- Basic banking transaction logic.

## 🔮 Future Enhancements

- Money transfer between accounts.
- OTP-based authentication.
- Account statement download.
- Admin dashboard.
- Improved account security.
- User profile management.

## ⚠️ Disclaimer

This project is developed for educational and learning purposes only. It is a banking simulation and is **not intended for real financial transactions or production banking use**.

## 👨‍💻 Author

**Saravanan**

Python Developer

---

⭐ If you find this project useful, please give this repository a star!
