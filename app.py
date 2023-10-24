from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

from flask_admin import Admin, AdminIndexView, expose, BaseView
from datetime import datetime
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcxzhjghehger'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:B20DCVT009@localhost/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
admin = Admin(app, name='Quản trị người dùng', template_mode='bootstrap3')

# Định nghĩa lớp Python ánh xạ bảng "course"
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    img = db.Column(db.String(255), nullable=False)
    price = db.Column(db.String(255), nullable=False)
    time_start = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    student = db.Column(db.Integer, nullable=True)
    def __str__(self):
        return self.title   # Giả sử student có thể là null


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    link = db.Column(db.String(255), nullable=True)
    # Các trường thông tin khác cho video
    course = db.relationship('Course', backref='videos')
    def __str__(self):
        return self.title 



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    role = db.Column(db.String(20))
    def __str__(self):
        return self.name
    

class CourseRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='registrations')
    course = db.relationship('Course', backref='registrations')
    def __str__(self):
        return self.user.name
    
class Controller(ModelView):
    def is_accessible(self):
        if current_user.role=='admin':
            return current_user.is_authenticated
        else:
            return abort (404)
    def not_authorized(self):
        return "You are not allowed to"

# Cấu hình các model view


class CourseView(ModelView):
    can_view_details = True
    edit_modal = True
    can_create = True
    details_modal= True
    column_exclude_list= ['img']
    column_searchable_list= ['price', 'title', 'description']
    column_labels = {
        'price':'Học phí',
        'title':'Tiêu đề',
        'description':'Mô tả',
        'time_start':'Khai giảng',
        'student': 'Sĩ số',
    }


class VideoView(ModelView):
    edit_modal = True
    details_modal = True

class registrationView(ModelView):
    can_create = False
    can_edit = False




#tạo các view
admin.add_view(Controller(User, db.session, name='Người dùng')) 
admin.add_view(CourseView(Course,db.session, name='Khoá học'))
admin.add_view(registrationView(CourseRegistration, db.session, name='Đăng ký'))
admin.add_view(VideoView(Video,db.session , name='Danh sách bài học'))



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('home.html')

@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/video')
def video():
    return render_template('video.html')


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
    if current_user.is_authenticated:
        return redirect(url_for('user_profile'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            if user.role == 'admin':
                return redirect('/admin/')
            else:
                return redirect(url_for('user_profile'))
        flash('Invalid email or password', 'error')
    return render_template('login.html')




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


@app.route('/join_course/<int:course_id>')
@login_required
def join_course(course_id):
    course = Course.query.get(course_id)
    if course:
        registration = CourseRegistration(user_id=current_user.id, course_id=course_id)
        db.session.add(registration)
        course.student += 1  # Tăng số lượng sinh viên của khoá học lên 1
        db.session.commit()
        videos = Video.query.filter_by(course_id=course_id).all()
        flash('Successfully joined the course.', 'success')
        return render_template('video.html', course=course, videos=videos)
    else:
        flash('Course not found.', 'error')
        return redirect(url_for('courses'))



@app.route('/course')
@login_required  # Đảm bảo rằng người dùng đã đăng nhập để kiểm tra đăng ký
def course():
    courses = Course.query.all()
    user = current_user  # Sử dụng current_user từ Flask-Login để lấy thông tin người dùng hiện tại
    
    # Tạo một danh sách khoá học mà người dùng đã đăng ký
    registered_courses = [registration.course for registration in user.registrations]
    
    return render_template('course.html', courses=courses, registered_courses=registered_courses)


@app.route('/course/<int:course_id>/video')
def course_video(course_id):
    course = Course.query.get(course_id)
    if course:
        videos = course.videos
        return render_template('video.html', course=course, videos=videos)
    else:
        flash('Không tìm thấy khoá học.', 'error')
        return redirect(url_for('course'))



# Trong route course_detail
@app.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get(course_id)
    if course:
        videos = course.videos
    if course:
        is_registered = False
        if current_user.is_authenticated:  # Kiểm tra xem người dùng đã đăng nhập chưa
            for registration in current_user.registrations:
                if registration.course_id == course_id:
                    is_registered = True
                    break
        return render_template('course_detail.html', course=course,videos=videos, is_registered=is_registered)
    else:
        flash('Không tìm thấy khoá học.', 'error')
        return redirect(url_for('courses'))

  

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        # Thực hiện tìm kiếm các khoá học có liên quan dựa trên `search_query` và title của video
        search_results = Course.query.join(Video).filter(
            (Course.title.ilike(f"%{search_query}%")) |
            (Video.title.ilike(f"%{search_query}%"))
        ).all()
        return render_template('course.html', courses=search_results)
    return redirect(url_for('courses'))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
