from flask import Flask
from flask_restx import Api
from .course.views import course_namespace, student_course_Namespace
from .auth.views import auth_namespace
from .config.config import config_dict
from .utils import db
from .models.user import User
from .models.courses import Student, Course, StudentCourse
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from .student.views import student_namespace


def create_app(config=config_dict['dev']):
    app = Flask(__name__)

    app.config.from_object(config)
    api = Api(app,
              title="Student-Management-System",
              description="A REST API for Student Management")

    api.add_namespace(student_namespace, path='student')
    api.add_namespace(course_namespace, path='/course')
    api.add_namespace(auth_namespace, path='/auth')
    db.init_app(app)
    jwt = JWTManager(app)

    migrate = Migrate(app, db)

    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'Course': Course,
            'Student': Student,
            'StudentCourse': StudentCourse

        }

    return app
