import json
import unittest
from .. import create_app
from ..config.config import config_dict
from ..models.courses import Course, Student, StudentCourse
from ..utils import db
from http import HTTPStatus
from flask_jwt_extended import create_access_token


class CourseTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config=config_dict['testing'])
        self.appctx = self.app.app_context()

        self.appctx.push()

        self.client = self.app.test_client()

        db.create_all()

    def tearDown(self):
        db.drop_all()
        self.app = None
        self.appctx.pop()
        self.client = None

    def test_create_course(self):
        course_data = {
            'id': 'PY101',
            'name': 'Introduction to python',
            'teacher': 'Tinubu'
        }

        access_token = create_access_token(identity='testuser')
        headers = {'Authorization': f'Bearer {access_token}'}

        response = self.client.post('/course/courses/create', json=course_data, headers=headers)
        response_data = response.get_json()

        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(response_data['message'], 'Course created successfully')

        created_course = Course.query.filter_by(id='PY101').first()
        self.assertIsNotNone(created_course)
        self.assertEqual(created_course.id, 'PY101')
        self.assertEqual(created_course.name, 'Introduction to python')
        self.assertEqual(created_course.teacher, 'Tinubu')

    def test_register_student(self):
        course = Course(id='COMP101', name='Introduction to Computer Science', teacher='Tinubu')
        db.session.add(course)
        db.session.commit()

        student = Student(name='John Doe', email='johndoe@example.com', phone='123-456-7890')
        db.session.add(student)
        db.session.commit()

        response = self.client.post(f'/course/courses/{course.id}/register',
                                    json={'student_id': student.id})
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

    def test_grade_course(self):
        course = Course(id='PY101', name='Introduction to Python', teacher='Tinubu')
        student = Student(id='101', name='clack', email='clack@gmail.com')
        db.session.add(course)
        db.session.add(student)
        db.session.commit()

        student_course = StudentCourse(student_id='101', course_id='PY101')
        db.session.add(student_course)
        db.session.commit()

        access_token = create_access_token(identity='testuser')
        headers = {'Authorization': f'Bearer {access_token}'}
        payload = {'grade': 75}
        response = self.client.post(f'/course/students/{student.id}/courses/{course.id}/grade', json=payload,
                                    headers=headers)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.get_json()['message'], 'Course graded successfully')

        student_course = StudentCourse.query.filter_by(student_id='101', course_id='PY101').first()
        self.assertEqual(student_course.grade, 75)

    def test_get_with_existing_student(self):
        course = Course(id='COMP101', name='Introduction to Computer Science', teacher='Tinubu')
        db.session.add(course)

        student = Student(id=1, name='clack', email='clack@gmail.com')
        db.session.add(student)

        student_course = StudentCourse(student_id=student.id, course_id=course.id, grade=70)
        db.session.add(student_course)

        db.session.commit()

        response = self.client.get('/course/students/1/courses/COMP101/grade')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['gpa'], 2.7)

    def test_get_with_nonexistent_student(self):
        # Calculate GPA for a non-existent student
        response = self.client.get('/course/students/999/courses/COMP101/grade')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(data['message'], 'No courses found for student')

    def test_get_with_student_with_no_grades(self):
        course = Course(id='COMP101', name='Introduction to Computer Science', teacher='Tinubu')
        student = Student(id=1, name='clack', email='clack@gmail.com')
        db.session.add_all([course, student])
        db.session.commit()

        student_course = StudentCourse(student_id=student.id, course_id=course.id, grade=92)
        db.session.add(student_course)
        db.session.commit()

        response = self.client.get('/course/students/1/courses/COMP101/grade')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(data[0]['gpa'], 4.0)

    def test_get_course_students_list(self):
        courses = Course(id='com101', name='Test Course', teacher='tinubu')
        db.session.add(courses)
        db.session.commit()

        students = Student(id=1, name='Test Student', email='test@student.com', phone='123456789')
        db.session.add(students)
        db.session.commit()

        student_course = StudentCourse(student_id=students.id, course_id=courses.id, grade=80)
        db.session.add(student_course)
        db.session.commit()

        response = self.client.get(f'/course/courses/{courses.id}/students')

        assert response.status_code == 200
