from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import hashlib
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this in production!

# Configure upload settings
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Root route with redirect to login
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, hashed_password)
        ).fetchone()
        conn.close()
        
        if user:
            flash('Login successful!')
            return redirect(url_for('home', user_id=user['id']))
        else:
            flash('Invalid credentials!')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        address = request.form.get('address')
        
        # Handle file upload
        uploaded_file = request.files.get('file')
        word_count = 0
        
        if uploaded_file and uploaded_file.filename.endswith('.txt'):
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            
            filename = f"{username}_{uploaded_file.filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    words = content.split()
                    word_count = len(words)
            except Exception as e:
                flash(f'Error processing file: {str(e)}')
                return redirect(url_for('register'))

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO users (username, password, firstname, lastname, email, address, word_count)'
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (username, hashed_password, firstname, lastname, email, address, word_count)
            )
            conn.commit()
            
            user = conn.execute(
                'SELECT * FROM users WHERE username = ?',
                (username,)
            ).fetchone()
            conn.commit()
            conn.close()
            
            flash('Registration and login successful!')
            return redirect(url_for('home', user_id=user['id']))
        except sqlite3.IntegrityError:
            flash('Username already exists!')
            return redirect(url_for('register'))
        
    return render_template('register.html')

@app.route('/home/<int:user_id>')
def home(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    
    if user:
        return render_template('home.html', user=user)
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)