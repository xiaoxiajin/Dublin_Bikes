from flask import render_template, request, redirect, url_for, flash, session

# Mock user data for demonstration
USERS = {
    "admin@gmail.com": "password123",
    "user@gmail.com": "mypassword"
}

def root():
    return render_template('index.html', username=session.get('username'))

def about():
    return render_template('about.html', username=session.get('username'))

def how_to_use():
    return render_template('use.html', username=session.get('username'))

def stations():
    return render_template('station.html', username=session.get('username'))

def contact():
    return render_template('contact.html', username=session.get('username'))

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # validation
        if username in USERS and USERS[username] == password:
            session['username'] = username
            session['logged_in'] = True  
            flash(f'Login successful! {username}', 'success')
            return redirect(url_for('root'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

def sign_up():
    return render_template('sign-up.html')