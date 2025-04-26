from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from functools import wraps
import sqlite3
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = 'Kvvr@2001'
app.jinja_env.globals.update(now=datetime.now)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def db_connection():
    conn = sqlite3.connect('data.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

class User(UserMixin):
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['password'], user['role'])
    return None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Admins only!', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and user['password'] == password:
            login_user(User(user['id'], user['username'], user['password'], user['role']))
            return redirect(url_for('home'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'librarian')

        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            flash("Username already exists. Choose another.", "danger")
            return redirect(url_for('signup'))

        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (username, password, role))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM books")
    total_books = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM members")
    total_members = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM borrow_records WHERE return_date IS NULL OR return_date = ''")
    total_borrowed = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM borrow_records
        WHERE (return_date IS NULL OR return_date = '') AND due_date < DATE('now')
    """)
    total_overdue = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return render_template('home.html', user=current_user,
                           total_books=total_books,
                           total_members=total_members,
                           total_borrowed=total_borrowed,
                           total_overdue=total_overdue)

@app.route('/books')
@login_required
def books():
    conn = db_connection()
    cursor = conn.cursor()
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
        cursor.execute("INSERT INTO books (title, author, isbn, quantity) VALUES (?, ?, ?, ?)",
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
    cursor = conn.cursor()
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        quantity = request.form['quantity']
        cursor.execute("UPDATE books SET title=?, author=?, isbn=?, quantity=? WHERE id=?",
                       (title, author, isbn, quantity, book_id))
        conn.commit()
        flash('Book updated!', 'success')
        return redirect(url_for('books'))
    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_book.html', book=book)

@app.route('/delete_book/<int:book_id>')
@login_required
def delete_book(book_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Book deleted.', 'warning')
    return redirect(url_for('books'))

@app.route('/members')
@login_required
def members():
    conn = db_connection()
    cursor = conn.cursor()
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
        cursor.execute("INSERT INTO members (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
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
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        cursor.execute("UPDATE members SET name=?, email=?, phone=? WHERE id=?", (name, email, phone, member_id))
        conn.commit()
        flash('Member updated!', 'success')
        return redirect(url_for('members'))
    cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
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
    cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Member deleted.', 'warning')
    return redirect(url_for('members'))

@app.route('/borrow')
@login_required
def borrow():
    conn = db_connection()
    cursor = conn.cursor()
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

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    books = []
    if request.method == 'POST':
        keyword = request.form['keyword']
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ?", (f'%{keyword}%', f'%{keyword}%'))
        books = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('search.html', books=books)

if __name__ == '__main__':
    app.run(debug=True)
