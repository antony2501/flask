from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:B20DCVT009@localhost/mydb'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    role = db.Column(db.String(20))

admin.add_view(ModelView(User, db.session)) 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'admin':
                return redirect('/admin/')
            else:
                return redirect(url_for('user_profile'))
        flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/admin')
def admin_panel():
    return redirect('/admin/')

@app.route('/user_profile')
@login_required
def user_profile():
    # Truy cập trang hồ sơ người dùng ở đây
    return render_template('user_profile.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = 'user'  # Set default role as 'user'
        
        # Kiểm tra xem email đã tồn tại hay chưa
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please use a different email.', 'error')
            return render_template('register.html')
        
        # Tiến hành đăng ký
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(name=name, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True)
