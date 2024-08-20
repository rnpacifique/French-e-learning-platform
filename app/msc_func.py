from app.models import User, Course
def add_course_to_user_internal(email, course_id):
    print('this is the course ID', course_id)
    user = User.get_by_email_enroll(email)
    if not user:
        raise ValueError('Invalid email')

    User.add_course_to_user(email, course_id)