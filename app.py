# Flask Application with MongoDB for User Authentication and Document Sharing

# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'Subha@123'
bcrypt = Bcrypt(app)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['user_management']
users_collection = db['users']
grades_collection = db['grades']

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        if users_collection.find_one({'email': email}):
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))

        users_collection.insert_one({'username': username, 'email': email, 'password': password})
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({'email': email})

        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            return redirect(url_for('dashboard'))

        flash('Invalid email or password!', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        grades = grades_collection.find({'user_id': session['user_id']})
        return render_template('dashboard.html', username=session['username'], grades=grades)

    flash('Please log in to access the dashboard.', 'warning')
    return redirect(url_for('login'))

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'user_id' not in session:
        flash('Please log in to update your profile.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        users_collection.update_one({'_id': session['user_id']}, {'$set': {'username': username}})
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    user = users_collection.find_one({'_id': session['user_id']})
    return render_template('update_profile.html', user=user)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'user_id' not in session:
        flash('Please log in to reset your password.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_password = bcrypt.generate_password_hash(request.form['new_password']).decode('utf-8')
        users_collection.update_one({'_id': session['user_id']}, {'$set': {'password': new_password}})
        flash('Password reset successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('reset_password.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)