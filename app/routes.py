from flask import Blueprint, redirect, url_for, session, render_template, current_app, flash,get_flashed_messages,jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Course
from app.forms import RegistrationForm, LoginForm, Enroll
from app.link_handler import get_src

main = Blueprint('main', __name__)

# Define the routes for the main blueprint
@main.route('/')
def index():
    return render_template('landing.html')


@main.route('/dash')
@login_required
def dashboard():
    name = current_user.name
    user_id = current_user.id
    user_email = current_user.email
    user_marks = User.get_user_marks(user_email)
    # print('this is the user marks', user_marks)
    # print('this is the user email', user_email)
    
    
    course_ids = User.get_user_courses(user_email)
    # print('this is the course ids', course_ids)
    courses = []    
    for course_id in course_ids:
        course = Course.get_course(course_id)
        course['src'] = get_src(course['embed_link'])
        courses.append(course)
    
    courses_marks = []
    if user_marks:
        for mark in user_marks:
            course = Course.get_course(mark['course_id'])
            courses_marks.append({'course': course, 'marks': mark['marks']})
            
    # print('this is courses marks', courses_marks)
    # print('this is course in courses marks', courses_marks[0]['course'])
    
        
        # print('in routes course', course['src'])

    # print(' this is the user email', user_email)
    # print('I should print courses here', courses)

    return render_template('student/dashboard.html', courses=courses, name=name, user_id=user_id, user_email=user_email, courses_marks=courses_marks)

@main.route('/chat')
@login_required
def chatbot():
    return render_template('student/chatbot.html')

@main.route('/learning')
@login_required
def learning():
    return render_template('student/learning.html')

@main.route('/test')
@login_required
def test():
    email = current_user.email
    name = current_user.name
    courses = User.get_user_courses(email) or []
    # course_dict = {}
    # course_dict[f'{name}\'s courses'] = courses or {}
    return render_template('student/test.html', courses=courses, name=name, email=email)

# TODO: Check why it is not validating  
@main.route('/courses', methods=['GET', 'POST'])
def courses(email=None, course_id=None):
    enroll = Enroll()
    if enroll.validate_on_submit():
        email = enroll.email.data
        User.add_course_to_user(email, course_id)
    # print("didnt validate the form") 
    courses = Course.get_all_courses()
    return render_template('student/courses.html', courses=courses, enroll=enroll)

@main.route('/liked_courses')
def liked_courses():
    return render_template('student/liked-course.html')

@main.route('/notification')
def notification():
    return render_template('student/notification.html')


@main.route('/auth', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        role = form.role.data
        existing_user = User.get_by_email(email)
        if existing_user is None:
            user = User.create(name, email, password, role)
            login_user(user)
            if role == 'student':
                return redirect(url_for('main.dashboard'))
            elif role == 'teacher':
                return redirect(url_for('main.dashboard_teacher'))
        else:
            flash('A user with that email already exists.')
    login_form = LoginForm()
    flash_messages = get_flashed_messages(with_categories=True)
    return render_template('auth.html', register_form=form, login_form=login_form, flash_messages=flash_messages)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user and user.check_password(form.password.data):
            user_json = user.user_to_json()
            print('this is the user json', user_json)          
            login_user(user)
            if user_json['role'] == 'student':
                print('this is the user role', user.role )
                return redirect(url_for('main.dashboard'))
            elif user_json['role'] == 'teacher':
                print('this is the user role', user.role )
                return redirect(url_for('main.dashboard_teacher'))
            elif user_json['role'] == None:
                flash('Please Sign up')
            print('after all the checks')
        else:
            flash('Invalid email or password.')
    register_form = RegistrationForm()
    flash_messages = get_flashed_messages(with_categories=True)
    return render_template('auth.html', register_form=register_form, login_form=form, flash_messages=flash_messages)
    # return render_template('login.html', register_form=register_form, login_form=form)

# Google login
@main.route('/login-google')
def login_google():
    google = current_app.config['oauth_google']
    redirect_uri = url_for('main.authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@main.route('/auth/callback')
def authorize():
    google = current_app.config['oauth_google']
    token = google.authorize_access_token()
    userinfo = google.parse_id_token(token)
    user = User.get(userinfo['sub'])
    if not user:
        user = User.create(userinfo['sub'], userinfo['name'], userinfo['email'])
    session['user'] = {'id': userinfo['sub'], 'name': userinfo['name'], 'email': userinfo['email']}
    login_user(user)
    return redirect(url_for('main.dashboard'))

@main.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user', None)
    return redirect(url_for('main.index'))

# teachers routes
####

#
######
#
#
#
#
#
#
#
#######

@main.route('/dashboard-teacher')
@login_required
def dashboard_teacher():
    all_students = User.get_all_users()
    my_courses = User.get_user_courses(current_user.email)

    course_names = []
    for course in my_courses:
        course = Course.get_course(course)
        course_names.append(course)
        
        
    my_students = []
    for student in all_students:
        if student['role'] == 'student':
            for course in student['courses']:
                if course in my_courses:
                    my_students.append(student)
                    break
    
    print('COURSE NAMES', course_names)

    return render_template('teacher/dashboard-teacher.html', my_students=my_students, course_names=course_names)


@main.route('/students')
def students():
    users = User.get_all_users()
    for user in users:
        if user['email'] == current_user.email:
            user_info = user
        user_courses = user_info['courses']
        courses = []
        for course in user_courses:
            course = Course.get_course(course)
            courses.append(course)
        print('this is the courses', courses)
    return render_template('teacher/students.html',user_courses=courses)

@main.route('/add-courses')
def add_courses():
    
    return render_template('teacher/upload-course.html')

@main.route('/send-notification')
def notify():
    return render_template('teacher/send-notification.html')


##
#
#
###
@main.route('/settings')
def settings():
    current_user = User.get(session['_user_id'])
    print('this is the current user', current_user)
    user_json = current_user.user_to_json()
    role = current_user.marks # the simple fix...
    return render_template('settings.html', role=role)

 