from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from functools import wraps
import mysql.connector
from datetime import datetime, date, timedelta


app = Flask(__name__)
app.secret_key = 'Kvvr@2001'
app.jinja_env.globals.update(now=datetime.now)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


def db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Kvvr@2001",
        database="librarydb"
    )


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


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Admins only!', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        username = request.form['username']
        password = request.form['password']
        role = 'librarian'  # Default role

        conn = db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            flash("Username already exists. Choose another.", "danger")
            return redirect(url_for('signup'))

        cursor.execute("INSERT INTO users (name, email, phone, username, password, role) VALUES (%s, %s, %s, %s, %s, %s)",
                       (name, email, phone, username, password, role))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and user['password'] == password:
            login_user(User(user['id'], user['username'], user['password'], user['role']))
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def home():
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM books")
    total_books = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM members")
    total_members = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM borrow_records WHERE return_date IS NULL")
    total_borrowed = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM borrow_records WHERE return_date IS NULL AND due_date < CURDATE()")
    total_overdue = cursor.fetchone()['total']

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
        cursor = conn.cursor(dictionary=True)

        # Check if book already exists (by title and author)
        cursor.execute("SELECT * FROM books WHERE title = %s AND author = %s", (title, author))
        existing_book = cursor.fetchone()

        if existing_book:
            # Update quantity if book already exists
            cursor.execute("UPDATE books SET quantity = quantity + %s WHERE id = %s", (quantity, existing_book['id']))
            flash('Book already exists. Quantity updated!', 'info')
        else:
            # Insert new book
            cursor.execute("INSERT INTO books (title, author, isbn, quantity) VALUES (%s, %s, %s, %s)",
                           (title, author, isbn, quantity))
            flash('New book added!', 'success')

        conn.commit()
        cursor.close()
        conn.close()
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


@app.route('/lend', methods=['GET', 'POST'])
@login_required
def lend_book():
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, title FROM books WHERE quantity > 0")
    books = cursor.fetchall()

    cursor.execute("SELECT id, name FROM members")
    members = cursor.fetchall()

    if request.method == 'POST':
        book_id = request.form['book_id']
        member_id = request.form['member_id']
        borrow_date = date.today()
        due_date = borrow_date + timedelta(days=7)  # ✅ Correct way to add 7 days

        cursor.execute("INSERT INTO borrow_records (book_id, member_id, borrow_date, due_date) VALUES (%s, %s, %s, %s)",
                       (book_id, member_id, borrow_date, due_date))

        cursor.execute("UPDATE books SET quantity = quantity - 1 WHERE id = %s", (book_id,))

        conn.commit()
        cursor.close()
        conn.close()
        flash('Book issued successfully!', 'success')
        return redirect(url_for('borrow'))

    cursor.close()
    conn.close()
    return render_template('lend_book.html', books=books, members=members)


@app.route('/return_book/<int:record_id>')
@login_required
def return_book(record_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE borrow_records SET return_date = CURDATE() WHERE id = %s", (record_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Book marked as returned.', 'success')
    return redirect(url_for('borrow'))


@app.route('/add_user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            flash('Username already exists. Choose another.', 'danger')
            return redirect(url_for('add_user'))

        cursor.execute("INSERT INTO users (name, email, phone, username, password, role) VALUES (%s, %s, %s, %s, %s, %s)",
                       (name, email, phone, username, password, role))
        conn.commit()
        cursor.close()
        conn.close()
        flash('New user added successfully.', 'success')
        return redirect(url_for('manage_users'))

    return render_template('add_user.html')


@app.route('/users')
@login_required
@admin_required
def manage_users():
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) AS total FROM users WHERE role = 'admin'")
    total_admins = cursor.fetchone()['total']

    cursor.close()
    conn.close()
    return render_template('manage_users.html', users=users, total_admins=total_admins)


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        cursor.execute("UPDATE users SET name=%s, email=%s, phone=%s, username=%s, password=%s, role=%s WHERE id=%s",
                       (name, email, phone, username, password, role, user_id))
        conn.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('manage_users'))

    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_user.html', user=user)


@app.route('/delete_user/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('User deleted successfully.', 'warning')
    return redirect(url_for('manage_users'))


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
        cursor = conn.cursor(dictionary=True)

        # Check if member already exists (by name and email)
        cursor.execute("SELECT * FROM members WHERE name = %s AND email = %s", (name, email))
        existing_member = cursor.fetchone()

        if existing_member:
            flash('Member already exists!', 'danger')
            return redirect(url_for('members'))

        cursor.execute("INSERT INTO members (name, email, phone) VALUES (%s, %s, %s)", (name, email, phone))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Member added successfully!', 'success')
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


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    books = []
    if request.method == 'POST':
        keyword = request.form['keyword']
        conn = db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM books WHERE title LIKE %s OR author LIKE %s", (f"%{keyword}%", f"%{keyword}%"))
        books = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('search.html', books=books)


if __name__ == '__main__':
    app.run(debug=True)
