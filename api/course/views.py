from flask_restx import Resource, Namespace, fields
from http import HTTPStatus
from flask_jwt_extended import jwt_required
from flask import request
from ..models.courses import Student, Course, StudentCourse
from ..utils import db
from ..student.views import calculate_grade_point

course_namespace = Namespace('course', description="Namespace for course ")
student_course_Namespace = Namespace('student_course', description="Namespace for Student_Course")

course_model = course_namespace.model(
    'Course', {
        'id': fields.Integer(required=True, description='The course unique identifier'),
        'name': fields.String(required=True, description='The course name'),
        'teacher': fields.String(required=True, descroption='Name of teacher for that course')
    }
)

grade_model = course_namespace.model('Grade', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a grade'),
    'student_id': fields.Integer(required=True, description='The unique identifier of the student'),
    'course_id': fields.String(required=True, description='The unique identifier of the course'),
    'grade': fields.Float(required=True, description='The grade earned by the student in the course')
})

student_course_model = student_course_Namespace.model('StudentCourse', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a student-course relationship'),
    'student_id': fields.Integer(required=True, description='The unique identifier of a student'),
    'course_id': fields.Integer(required=True, description='The unique identifier of a course'),
    'grade': fields.Float(required=False, description='The student\'s grade in the course (0.0 - 4.0)'),
})


@course_namespace.route('/courses/create')
class CreateCourse(Resource):
    @course_namespace.expect(course_model)
    @course_namespace.doc(
        description="Crate a New Course "
        
    ,
    )
    @jwt_required()
    def post(self):
        """
            Create a new course
        :return:
        """
        data = request.json

        course_id = data.get('id')
        if not course_id:
            return {'message': 'Course ID is required'}, HTTPStatus.BAD_REQUEST

        existing_course = Course.query.filter_by(id=course_id).first()
        if existing_course:
            return {'message': f'Course with ID {course_id} already exists'}, HTTPStatus.CONFLICT

        new_course = Course(
            id=course_id,
            name=data['name'],
            teacher=data['teacher']
        )

        db.session.add(new_course)
        db.session.commit()

        return {'message': 'Course created successfully'}, HTTPStatus.CREATED


@course_namespace.route('/courses/<string:course_id>/register')
class RegisterStudent(Resource):
    @course_namespace.expect(course_model)
    @course_namespace.doc(
        description="Register a student for a course "
    )
    @jwt_required()
    def post(self, course_id):
        """
            Register a student for a course
        :return:
        """
        data = request.json
        student_id = data['student_id']

        course = Course.query.get(course_id)
        student = Student.query.get(student_id)

        if not course or not student:
            return {'message': 'Course or student not found'}, HTTPStatus.NOT_FOUND

        # Check if the course already has the student registered
        if student in course.students:
            return {'message': 'Student already registered for the course'}, HTTPStatus.CONFLICT

        # Add the student to the course's list of students
        course.students.append(student)
        db.session.commit()

        return {'message': 'Student registered for the course successfully'}, HTTPStatus.CREATED


@course_namespace.route('/students/<int:student_id>/courses/<string:course_id>/grade')
class GradeCourse(Resource):
    @course_namespace.expect(grade_model)
    @course_namespace.doc(
        description="Grade a Student For a course "
    )
    @jwt_required()
    def post(self, student_id, course_id):
        """
        Grade a course for a student
        :param student_id:
        :param course_id:
        :return:
        """
        data = request.json
        grade = data['grade']

        student_course = StudentCourse.query.filter_by(student_id=student_id, course_id=course_id).first()

        if not student_course:
            return {'message': 'Student-course combination not found'}, HTTPStatus.NOT_FOUND

        student_course.grade = grade
        db.session.commit()

        return {'message': 'Course graded successfully'}, HTTPStatus.OK

    @staticmethod
    def get(student_id, course_id):
        """
        Calculate total grade point average (GPA) for a student in all courses.
        :param student_id: ID of the student whose GPA is to be calculated.
        :param course_id: ID of the course (not used).
        :return: A tuple containing a dictionary with the student's GPA and a status code.
        """
        student_courses = StudentCourse.query.filter_by(student_id=student_id).all()

        if not student_courses:
            return {'message': 'No courses found for student'}, HTTPStatus.NOT_FOUND

        total_grade_points = 0
        total_courses = 0

        for student_course in student_courses:
            grade = student_course.grade

            if not grade:
                continue

            grade_point = calculate_grade_point(grade)
            total_grade_points += grade_point
            total_courses += 1

        if total_courses == 0:
            return {'message': 'No grades found for student'}, HTTPStatus.NOT_FOUND

        gpa = total_grade_points / total_courses
        gpa = round(gpa, 2)

        return [{'gpa': gpa}], HTTPStatus.OK


@course_namespace.route('/courses/<string:course_id>/students')
class CourseStudentsList(Resource):
    @course_namespace.marshal_with(student_course_model)
    @course_namespace.doc(
        description="Retrieve all students registered for a course "
    )
    @jwt_required()
    def get(self, course_id):
        """
        Retrieve all students registered for a particular course
        """
        student_courses = StudentCourse.query.filter_by(course_id=course_id).all()

        # Create a list of dictionaries with information about each student
        student_list = []
        for student_course in student_courses:
            student = student_course.student
            student_dict = {
                'id': student.id,
                'name': student.name,
                'email': student.email,
                'phone': student.phone,
                'grade': student_course.grade
            }
            student_list.append(student_dict)

        return student_list, HTTPStatus.OK
