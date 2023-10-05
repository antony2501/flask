from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin import Admin
from datetime import datetime
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:B20DCVT009@localhost/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')

# Định nghĩa lớp Python ánh xạ bảng "course"
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    img = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    time_start = db.Column(db.Date, nullable=False)
    student = db.Column(db.Integer, nullable=True)  # Giả sử student có thể là null

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    role = db.Column(db.String(20))

class CourseRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='registrations')
    course = db.relationship('Course', backref='registrations')


admin.add_view(ModelView(User, db.session)) 



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/bae1')
def bae1():
    return render_template('base1.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/course')
def course():
    courses = Course.query.all()
    for course in courses:
        print(f"Course ID: {course.id}, Title: {course.title}, Image: {course.img}, Price: {course.price}, Start Date: {course.time_start}, Student: {course.student}")
        
    return render_template('course.html', courses=courses)

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
        
        new_user = User(name=name, email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:  # So sánh mật khẩu dưới dạng văn bản thô
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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


from datetime import datetime

@app.route('/join_course/<int:course_id>', methods=['GET', 'POST'])

@login_required
def join_course(course_id):
    course = Course.query.get(course_id)
    if course:
        registration = CourseRegistration(user_id=current_user.id, course_id=course_id)
        db.session.add(registration)
        db.session.commit()
        flash('Successfully joined the course.', 'success')
    else:
        flash('Course not found.', 'error')
    return redirect(url_for('courses'))



if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
