from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'correspondent', 'principal', 'admin'

# Initialize the database
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            if user.role == 'correspondent':
                return redirect(url_for('correspondent_dashboard'))
            elif user.role == 'principal':
                return redirect(url_for('principal_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/correspondent_dashboard')
@login_required
def correspondent_dashboard():
    if current_user.role != 'correspondent':
        return redirect(url_for('login'))
    return render_template('correspondent_dashboard.html')

@app.route('/principal_dashboard')
@login_required
def principal_dashboard():
    if current_user.role != 'principal':
        return redirect(url_for('login'))
    return render_template('principal_dashboard.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':  # Only admin can access this route
        return redirect(url_for('login'))
    users = User.query.all()  # Fetch all users from the database
    return render_template('admin_dashboard.html', users=users)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)