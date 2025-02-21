from flask import Flask, session, request, jsonify, render_template

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required to encrypt the session data

# Mock user database
users = {
    'Anush': {'password': 'anush123', 'name': 'Anush'},
    'Billie': {'password': 'billie123', 'name': 'Billie'},
    'Claire': {'password': 'claire123', 'name': 'Claire'}
}

# Home route to serve login page
@app.route('/')
def home():
    return render_template('login.html') 

# Login route
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Check if the user exists and the password is correct
    if username in users and users[username]['password'] == password:
        # Store the username in the session to keep the user logged in
        session['username'] = username
        return jsonify({'message': 'Login successful!'})
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

# Protected route that requires authentication
@app.route('/profile')
def profile():
    # Check if the user is logged in by looking at the session
    if 'username' in session:
        username = session['username']
        user_name = users[username]['name']
        return jsonify({'message': f'Welcome to your profile, {user_name}!'})
    else:
        return jsonify({'error': 'You must be logged in to view this page'}), 403

# Logout route
@app.route('/logout')
def logout():
    # Remove the username from the session to log the user out
    session.pop('username', None)
    return jsonify({'message': 'You have been logged out.'})

if __name__ == '__main__':
    app.run(debug=True)