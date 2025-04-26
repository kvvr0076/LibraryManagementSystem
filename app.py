from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from functools import wraps
import mysql.connector
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = 'Kvvr@2001'
app.jinja_env.globals.update(now=datetime.now)  # Make datetime.now available in templates

# Configure login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Database connection
def db_connection():
    return mysql.connector.connect(
        host="sql3.freesqldatabase.com",
        user="sql3775460",
        password="Yh6x3YCMuu",
        database="sql3775460",
        port=3306
    )


# User class for login
class User(UserMixin):
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role


@login_manager.user_loader
def load_user(user_id):
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['password'], user['role'])
    return None


# Role-based decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Admins only!', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)

    return decorated_function


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            login_user(User(user['id'], user['username'], user['password'], user['role']))
            return redirect(url_for('home'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'librarian')

        conn = db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if username already exists
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            flash("Username already exists. Choose another.", "danger")
            return redirect(url_for('signup'))

        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                       (username, password, role))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')


# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Dashboard
@app.route('/')
@login_required
def home():
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM books")
    total_books = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM members")
    total_members = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM borrow_records WHERE return_date IS NULL")
    total_borrowed = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM borrow_records WHERE return_date IS NULL AND due_date < CURDATE()")
    total_overdue = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return render_template('home.html', user=current_user,
                           total_books=total_books,
                           total_members=total_members,
                           total_borrowed=total_borrowed,
                           total_overdue=total_overdue)


# Book Routes
@app.route('/books')
@login_required
def books():
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('books.html', books=books)


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        if current_user.role == 'librarian':
            flash('You are adding a book as a librarian.', 'info')

        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        quantity = request.form['quantity']
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO books (title, author, isbn, quantity) VALUES (%s, %s, %s, %s)",
                       (title, author, isbn, quantity))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Book added!', 'success')
        return redirect(url_for('books'))
    return render_template('add_book.html')


@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        quantity = request.form['quantity']
        cursor.execute("UPDATE books SET title=%s, author=%s, isbn=%s, quantity=%s WHERE id=%s",
                       (title, author, isbn, quantity, book_id))
        conn.commit()
        flash('Book updated!', 'success')
        return redirect(url_for('books'))
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_book.html', book=book)


@app.route('/delete_book/<int:book_id>')
@login_required
def delete_book(book_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Book deleted.', 'warning')
    return redirect(url_for('books'))


# Members
@app.route('/members')
@login_required
def members():
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('members.html', members=members)


@app.route('/add_member', methods=['GET', 'POST'])
@login_required
@admin_required
def add_member():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO members (name, email, phone) VALUES (%s, %s, %s)", (name, email, phone))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Member added!', 'success')
        return redirect(url_for('members'))
    return render_template('add_member.html')


@app.route('/edit_member/<int:member_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_member(member_id):
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        cursor.execute("UPDATE members SET name=%s, email=%s, phone=%s WHERE id=%s",
                       (name, email, phone, member_id))
        conn.commit()
        flash('Member updated!', 'success')
        return redirect(url_for('members'))
    cursor.execute("SELECT * FROM members WHERE id = %s", (member_id,))
    member = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_member.html', member=member)


@app.route('/delete_member/<int:member_id>')
@login_required
@admin_required
def delete_member(member_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members WHERE id = %s", (member_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Member deleted.', 'warning')
    return redirect(url_for('members'))


# Borrow/Return
@app.route('/borrow')
@login_required
def borrow():
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT br.id, b.title, m.name, br.borrow_date, br.return_date, br.due_date
        FROM borrow_records br
        JOIN books b ON br.book_id = b.id
        JOIN members m ON br.member_id = m.id
    """)
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    today = date.today()
    return render_template('borrow_return.html', records=records, today=today)


# Search
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    books = []
    if request.method == 'POST':
        keyword = request.form['keyword']
        conn = db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM books WHERE title LIKE %s OR author LIKE %s",
                       (f'%{keyword}%', f'%{keyword}%'))
        books = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('search.html', books=books)


# Run app
if __name__ == '__main__':
    app.run(debug=True)
