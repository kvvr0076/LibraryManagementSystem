# 📚 Library Management System (Flask + SQLite)

A full-stack **Library Management System** built with **Python Flask**, designed to simplify the management of books, members, and borrowing/return operations. The application follows the **MVC pattern**, using **Jinja2 templates** for the frontend and **SQLite** as the backend database.

---

## 🔧 Technologies Used

* **Programming Language:** Python 3.x
* **Framework:** Flask (Micro web framework)
* **Frontend:** HTML5, CSS3, Jinja2 Templates
* **Database:** SQLite3
* **Libraries:** Flask, SQLAlchemy, Werkzeug, WTForms
* **IDE:** VS Code / PyCharm
* **Version Control:** Git & GitHub

---

## ✅ Features

### 🔹 User Management

* Secure login and signup functionality
* Role-based access for admin and librarians
* Password hashing using **Werkzeug**

### 🔹 Book Management

* Add, edit, delete, and view books
* Search books by title, author, or ISBN
* Maintain availability and total count

### 🔹 Member Management

* Add and manage library members
* View borrowing history and active loans

### 🔹 Borrow & Return Module

* Record book issues and returns
* Track due dates and late submissions

### 🔹 Dashboard

* Overview of total books, members, and borrowed items
* Intuitive UI with role-specific navigation menus

---

## 🧠 Project Architecture

The system follows a simplified **MVC structure**:

* **Model (Database):** SQLite3 tables for users, books, and borrowed records.
* **View (Templates):** HTML pages built using **Jinja2** templating engine.
* **Controller (Routes):** Defined in `app.py`, handling HTTP requests and rendering templates.

---

## 🧩 Folder Structure

```
LibraryManagementSystem-master/
├── app.py                # Main Flask application
├── requirements.txt      # Dependencies
├── static/
│   └── style.css         # Custom styles
├── templates/            # Jinja2 templates
│   ├── add_book.html
│   ├── add_member.html
│   ├── add_user.html
│   ├── books.html
│   ├── borrow_return.html
│   ├── edit_book.html
│   ├── edit_member.html
│   ├── edit_user.html
│   ├── home.html
│   ├── layout.html
│   ├── lend_book.html
│   ├── login.html
│   ├── manage_users.html
│   ├── members.html
│   ├── search.html
│   └── signup.html
└── .idea/                # IDE config files
```

---

## ⚙️ Database Schema Overview

| Table              | Description                                                            |
| ------------------ | ---------------------------------------------------------------------- |
| **users**          | Stores admin and librarian credentials (username, password hash, role) |
| **books**          | Holds details like title, author, quantity, and category               |
| **members**        | Tracks registered library members                                      |
| **borrow_records** | Logs issued books with borrow/return dates                             |

---

## 🚀 How to Run Locally

1. **Clone the repository:**

   ```bash
   git clone https://github.com/kvvr0076/LibraryManagementSystem.git
   cd LibraryManagementSystem-master
   ```

2. **Set up a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask app:**

   ```bash
   python app.py
   ```

5. **Access the application:**

   ```
   http://127.0.0.1:5000/
   ```

---

## 🧪 Testing & Validation

* Manual testing for CRUD operations
* Input validation using WTForms
* Basic authentication and session management testing

---

## ☁️ Future Enhancements

* Integrate **Flask-Login** for advanced user sessions
* Add **email notifications** for overdue books
* Implement **pagination** and **search filters**
* Deploy on **Azure App Service** or **Render**
* Add RESTful **API endpoints** for external access

---

## 👨‍💻 Author

**Vishnuvardhan Reddy Komatireddy**
📅 Year: 2025

---

**Live Repository:** [https://github.com/kvvr0076/LibraryManagementSystem](https://github.com/kvvr0076/LibraryManagementSystem)

