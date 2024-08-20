"""this module contains the models for the application"""

from flask_login import UserMixin
from app import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from app.id_gen import generate_userID, generate_courseID, generate_notificationID
import uuid

class User(UserMixin):
    def __init__(self, id, name, email, password_hash=None, courses_id=None, courses=[], marks=None, role=None):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.courses = courses_id or []
        self.marks = marks or []
        self.role = role

    @staticmethod
    def get_all_users():
        users = []
        for user_doc in mongo.users.find():
            users.append(user_doc)
        return users

    @staticmethod 
    def get_user_courses(email):
        # print('using this email', email)
        user = User.get_by_email_enroll(email)
        # print('this is the user', user)
        return user['courses']
    
    
   
    @staticmethod
    def add_course_to_user(email, course_id):
        # print('I am adding this', course_id)
        user = User.get_by_email_enroll(email)
        if user:
            if 'courses' not in user:
                user['courses'] = []
            if course_id not in user['courses']:
                user['courses'].append(course_id)
                mongo.users.update_one({"_id": user["_id"]}, {"$set": {"courses": user['courses']}})
                print("Course added to user")
                print('this is the id of the updated', user["_id"])
        else:
            print("User not found")
    #addings marks        
    def add_marks_to_user(user_email, course_id, marks):
        # print('i reached the add function')
        user = User.get_by_email_enroll(user_email)
        # print('this is the user', user)
        if user:
            if 'marks' not in user:
                user['marks'] = []
            user['marks'].append({"course_id": course_id, "marks": marks})
            mongo.users.update_one({"_id": user["_id"]}, {"$set": {"marks": user['marks']}})
            user_marks = user['marks']
            # print('this is user marks', user['marks'])
            
            for user_mark in user_marks:
                if user_mark['course_id'] == course_id:
                    return "Marks already added"
                user_marks.append({"course_id": course_id, "marks": marks})
                mongo.users.update_one({"_id": user["_id"]}, {"$set": {"marks": user_marks}})
                print("Marks added to user")
        else:
            print("User not found")


    @staticmethod
    def get(user_id):
        user_doc = mongo.users.find_one({"_id": user_id})
        if user_doc:
            return User(user_doc.get("_id"), user_doc.get("name"), user_doc.get("email"), user_doc.get("password_hash"), user_doc.get("courses"),  user_doc.get("marks"), user_doc.get("role"))


     # this function is used when enrolling a user to a course
    @staticmethod
    def get_by_email_enroll(email):
        user_doc = mongo.users.find_one({"email": email})
        print('this is the user doc', user_doc)
        if user_doc:
            return user_doc
        return None
    
    
    #this function is used to get a user by email in login
    def get_by_email(email):
        user_doc = mongo.users.find_one({"email": email})
        if user_doc:
            return User(user_doc.get("_id"), user_doc.get("name"), user_doc.get("email"), user_doc.get("password_hash"), user_doc.get("courses"),   user_doc.get("marks"), user_doc.get("role"))
        return None
    
    @staticmethod
    def get_user_marks(user_email):
        user = User.get_by_email_enroll(user_email)
        return user['marks']
    

    @staticmethod
    def create(name, email, password, role, courses =[], marks=[]):
        _id = generate_userID()
        password_hash = generate_password_hash(password)
        user_doc = {
            "_id": _id,
            "name": name,
            "email": email,
            "password_hash": password_hash,
            "courses": [],
            "marks": [],
            "role": role
        }
        mongo.users.insert_one(user_doc)
        return User(_id, name, email, password_hash, courses=courses, marks=marks, role=role)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    
    def user_to_json(self):
        json = {
            "_id": self.id,
            "name": self.name,
            "email": self.email,
            "courses": self.courses,
            "marks": self.role, # simple fix correct this 
            "role": self.marks
        }
        print('this is the json', json)
        return json
    
 
# this the course model
#
#
#
#
#
#
#
#
#
#
#thr course model starts here
class Course:
    def __init__(self, _id, title, description=None, instructor=None, modules=None, link=None, student_enrolled=[]):
        self.id = _id
        self.title = title
        self.description = description
        self.instructor = instructor
        self.modules = modules
        self.link = link
        self.student_enrolled = student_enrolled
        
    def save(self):
        course_doc = {
            "_id": self.id,
            "title": self.title,
            "description": self.description,
            "instructor": self.instructor,
            "modules": self.modules,
            "embed_link": self.link,
            "student_enrolled": self.student_enrolled
        }
        mongo.courses.insert_one(course_doc)
        return self

    @staticmethod
    def get_course(course_id):
        course_doc = mongo.courses.find_one({'course_id': course_id})
        if not course_doc:
            return None
        return course_doc
    @staticmethod
    def is_course_valid(course_id):
        return Course.get_course(course_id) is not None

# class Course:
#     def __init__(self, id, title, description, instructor_id, modules):
#         self.id = id
#         self.title = title
#         self.description = description
#         self.instructor_id = instructor_id
#         self.modules = modules
        
    def is_course_valid(course_id):
        course = Course.get_course(course_id)
        return course is not None
    @staticmethod
    def get_all_courses():
        courses = []
        for course_doc in mongo.courses.find():
            courses.append(course_doc)
        return courses

    @staticmethod
    def get_course(course_id):
        course_doc = mongo.courses.find_one({"_id": course_id})
        if course_doc:
            return course_doc
            # return Course(
            #     course_doc["_id"],
            #     course_doc["title"],
            #     course_doc["description"],
            #     # course_doc["instructor"],
            #     course_doc["modules"]
            # )
        return None
    
    @staticmethod
    def get_course_by_name(title):
        course_doc = mongo.courses.find_one({"title": title})
        if course_doc:
            return Course(
                course_doc["_id"],
                course_doc["title"],
                course_doc["description"],
                course_doc["instructor"],
                course_doc["modules"]
            )
    @staticmethod        
    def get_course_by_instructor(instructor):
        course_doc = mongo.courses.find_one({"instructor": instructor})
        if course_doc:
            return Course(
                course_doc["_id"],
                course_doc["title"],
                course_doc["description"],
                course_doc["instructor_id"],
                course_doc["modules"]
            )
        return None

    @staticmethod
    def create(title, description, instructor, lessons, link, student_enrolled=[]):
        _id = generate_courseID()
        course_doc = {
            "title": title,
            "description": description,
            "instructor_id": instructor,
            "modules": lessons,
            "embed_link": link,
            "student_enrolled": student_enrolled if student_enrolled else []
        }
        return Course(_id, title, description, instructor, lessons, link, student_enrolled)

class Teacher:
    def __init__(self, id, name, email, password_hash=None):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash

    @staticmethod
    def get_all_teachers():
        teachers = []
        for teacher_doc in mongo.teachers.find():
            teachers.append(teacher_doc)
        return teachers

    @staticmethod
    def get_teacher(teacher_id):
        teacher_doc = mongo.teachers.find_one({"_id": teacher_id})
        if teacher_doc:
            return Teacher(teacher_doc["_id"], teacher_doc["name"], teacher_doc["email"], teacher_doc.get("password_hash"))
        return None

    @staticmethod
    def create(name, email, password):
        _id = generate_userID()
        password_hash = generate_password_hash(password)
        teacher_doc = {
            "_id": _id,
            "name": name,
            "email": email,
            "password_hash": password_hash
        }
        mongo.teachers.insert_one(teacher_doc)
        return Teacher(_id, name, email, password_hash)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

        
class Notification:
        def __init__(self, id, title, author, description):
            self.id = id
            self.title = title
            self.author = author
            self.description = description
    
        @staticmethod
        def get_all_notifications():
            notifications = []
            for notification_doc in mongo.notifications.find():
                notifications.append(notification_doc)
            return notifications
    
        @staticmethod
        def get_notification(notification_id):
            notification_doc = mongo.notifications.find_one({"_id": notification_id})
            if notification_doc:
                return notification_doc
            return 'Notification not found'
    
        @staticmethod
        def create(title, author, description):
            _id = generate_notificationID()
            notification_doc = {
                "title": title,
                "author": author,
                "description": description
            }
            return Notification(_id, title, author, description)
            
        def save(self):
            notification_doc = {
                "_id": self.id,
                "title": self.title,
                "author": self.author,
                "description": self.description
            }
            mongo.notifications.insert_one(notification_doc)
            return 'notification Addded'
 