CREATE DATABASE mydb;

create table user (
    id int not null auto_increment primary key,
    name varchar(255) not null,
    email varchar(255) unique not null,
    password varchar(255) not null,
    role varchar(255) not null,
)

CREATE TABLE course(
    id int not null auto_increment primary key,
    title varchar(255) not null,
    img varchar(255) not null,
    price int not null,
    time_start DATA NOT NULL,
    student INT
)

class CourseRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='registrations')
    course = db.relationship('Course', backref='registrations')


create DATABASE video_course(
    id int not null auto_increment primary key,
    titles varchar(255),
    link varchar(255),
    course_id INT,
    FOREIGN KEY ( course_id ) REFERENCES course(id)
)





