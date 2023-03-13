from flask import Flask
from flask_restx import Api
from .students.views import students_fields_schema,student_score_add_fields_schema,course_fields_schema,course_retrieve_fields_schema
from .auth.views import auth_namespace
from .students.views import students_namespace
from .config.config import config_dict
from .utils import db
from .models.courses import Course
from .models.studentcourse import StudentCourse
from .models.students import Student
from .models. users import User
from .models. grade import Score
from .models. teacher import Teacher
from .models. admin import Admin
from flask_migrate import Migrate


def create_app(config=config_dict['dev']):
    app=Flask(__name__)

    app.config.from_object(config)

    db.init_app(app)
    migrate=Migrate(app,db)

    api = Api(app)

    # api.add_namespace(student_score_add_fields_schema)
    # api.add_namespace(students_fields_schema)
    # api.add_namespace(course_retrieve_fields_schema)
    api.add_namespace(auth_namespace, path='/auth')
    api.add_namespace(students_namespace, path='/students')
    #api.add_namespace(courses_namespace, path='/courses')

    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'Student': Student,
            'Course': Course,
            'StudentCourse': StudentCourse,
            'Grade' : Score,
            'Teacher' : Teacher, 
            'Admin': Admin            
                 }

    return app