# Library Management System

A complete Library Management System built with Flask and MySQL, fully working offline on localhost.

## Features

- User Login/Signup (Admin and Librarian)
- Admin Panel (Full Access)
  - Manage Users (Add, Edit, Delete)
  - Manage Books (Add, Edit, Delete, Search)
  - Manage Members (Add, Edit, Delete)
  - Lend and Return Books
- Librarian Access
  - Add, Edit, Delete Books
  - Borrow/Return Books
- Borrow/Return Management
  - Auto-handle borrow dates, due dates, return dates
- Bootstrap 5 Frontend (Responsive and Clean)
- Flask-Login for user authentication
- MySQL Database integration (using localhost XAMPP)

## Technologies Used

- Python 3.8+
- Flask 3.0+
- Flask-Login
- Bootstrap 5
- MySQL (XAMPP Server)
- PyCharm IDE

## How to Run Locally

1. Install Required Packages:

   pip install -r requirements.txt

2. Start MySQL Server (via XAMPP)

3. Create Database:

- Database name: librarydb
- Tables:
  - users
  - books
  - members
  - borrow_records

4. Run Flask App:

   python app.py

5. Open in Browser:

   http://127.0.0.1:5000/

## Default Admin Credentials

- Username: admin
- Password: admin123

## Folder Structure

LibraryManagementSystem/
- app.py
- requirements.txt
- templates/
  - layout.html
  - login.html
  - signup.html
  - books.html
  - members.html
  - borrow_return.html
  - lend_book.html
  - manage_users.html
  - edit_book.html
  - edit_member.html
  - edit_user.html
  - home.html
  - search.html
- static/
  - style.css




## Important

- Admin can manage everything.
- Librarians can only manage Books and Borrow/Return.
- Duplicate handling is implemented (no duplicate users, books, members).
- Book stock management is auto-handled.
- Return date auto-updates on book return.

✅ Project Created and Maintained by: Vishnuvardhan Reddy Komatireddy
📅 Year: 2024
