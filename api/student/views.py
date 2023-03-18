from flask_restx import Resource, Namespace, fields
from flask import request
from http import HTTPStatus
from ..models.courses import Student
from ..utils import db
from flask_jwt_extended import jwt_required

student_namespace = Namespace('student', description="Namespace for student")


@student_namespace.route('/new_student')
@jwt_required()
class StudentList(Resource):
    new_student_model = student_namespace.model('NewStudent', {
        'name': fields.String(required=True, description='The name of the new student'),
        'email': fields.String(required=True, description='The email of the new student'),
        'phone': fields.String(required=False, description='The phone number of the new student')
    })

    student_response_model = student_namespace.model('StudentResponse', {
        'id': fields.Integer(required=True, description='The ID of the student'),
        'name': fields.String(required=True, description='The name of the student'),
        'email': fields.String(required=True, description='The email of the student'),
        'phone': fields.String(required=False, description='The phone number of the student')
    })

    error_model = student_namespace.model('Error', {
        'message': fields.String(required=True, description='The error message')
    })

    @student_namespace.expect(new_student_model)
    @student_namespace.response(HTTPStatus.CREATED, 'Student created successfully', student_response_model)
    @student_namespace.response(HTTPStatus.BAD_REQUEST, 'Validation error', error_model)
    @student_namespace.response(HTTPStatus.INTERNAL_SERVER_ERROR, 'Failed to create student', error_model)
    def post(self):
        """
        Create a new student
        """
        data = request.json

        if not data.get('name') or not data.get('email'):
            return {'message': 'Name and email are required'}, HTTPStatus.BAD_REQUEST

        new_student = Student(name=data['name'], email=data['email'], phone=data.get('phone'))

        try:
            # Add the new student to the database
            db.session.add(new_student)
            db.session.commit()
        except Exception as e:
            # Handle database errors
            db.session.rollback()
            return {'message': 'Failed to create student: {}'.format(str(e))}, HTTPStatus.INTERNAL_SERVER_ERROR

        # Return the new student object and a 201 status code
        return {
                   'id': new_student.id,
                   'name': new_student.name,
                   'email': new_student.email,
                   'phone': new_student.phone
               }, HTTPStatus.CREATED


@student_namespace.route('/students/<int:student_id>')
@jwt_required()
class Student(Resource):
    # Define the request model for updating a student
    update_student_model = student_namespace.model('UpdateStudent', {
        'name': fields.String(required=False, description='The updated name of the student'),
        'email': fields.String(required=False, description='The updated email of the student'),
        'phone': fields.String(required=False, description='The updated phone number of the student')
    })

    # Define the response models
    student_response_model = student_namespace.model('StudentResponse', {
        'id': fields.Integer(required=True, description='The ID of the student'),
        'name': fields.String(required=True, description='The name of the student'),
        'email': fields.String(required=True, description='The email of the student'),
        'phone': fields.String(required=False, description='The phone number of the student')
    })

    error_model = student_namespace.model('Error', {
        'message': fields.String(required=True, description='The error message')
    })

    @student_namespace.expect(update_student_model)
    @student_namespace.response(HTTPStatus.OK, 'Student updated successfully', student_response_model)
    @student_namespace.response(HTTPStatus.BAD_REQUEST, 'Validation error', error_model)
    @student_namespace.response(HTTPStatus.NOT_FOUND, 'Student not found', error_model)
    @student_namespace.response(HTTPStatus.INTERNAL_SERVER_ERROR, 'Failed to update student', error_model)
    def put(self, student_id):
        """
        Update an existing student
        """
        data = request.json

        # Get the student object from the database
        student = Student.query.get(student_id)

        # Return a 404 error if the student is not found
        if not student:
            return {'message': 'Student not found'}, HTTPStatus.NOT_FOUND

        # Update the student object with the data from the request
        if data.get('name'):
            student.name = data['name']
        if data.get('email'):
            student.email = data['email']
        if data.get('phone'):
            student.phone = data['phone']

        try:

            db.session.commit()
        except Exception as e:

            db.session.rollback()
            return {'message': 'Failed to update student: {}'.format(str(e))}, HTTPStatus.INTERNAL_SERVER_ERROR

        # Return the updated student object and a 200 status code
        return {
                   'id': student.id,
                   'name': student.name,
                   'email': student.email,
                   'phone': student.phone
               }, HTTPStatus.OK


@student_namespace.route('/students/<int:student_id>')
@jwt_required()
class Student(Resource):
    # Define the response models
    student_response_model = student_namespace.model('StudentResponse', {
        'id': fields.Integer(required=True, description='The ID of the student'),
        'name': fields.String(required=True, description='The name of the student'),
        'email': fields.String(required=True, description='The email of the student'),
        'phone': fields.String(required=False, description='The phone number of the student')
    })

    error_model = student_namespace.model('Error', {
        'message': fields.String(required=True, description='The error message')
    })

    @student_namespace.response(HTTPStatus.OK, 'Student deleted successfully', student_response_model)
    @student_namespace.response(HTTPStatus.NOT_FOUND, 'Student not found', error_model)
    @student_namespace.response(HTTPStatus.INTERNAL_SERVER_ERROR, 'Failed to delete student', error_model)
    def delete(self, student_id):
        """
        Delete an existing student
        """
        student = Student.query.get(student_id)

        if not student:
            return {'message': 'Student not found'}, HTTPStatus.NOT_FOUND

        try:
            # Delete the student object from the database
            db.session.delete(student)
            db.session.commit()
        except Exception as e:
            # Handle database errors
            db.session.rollback()
            return {'message': 'Failed to delete student: {}'.format(str(e))}, HTTPStatus.INTERNAL_SERVER_ERROR

        # Return the deleted student object and a 200 status code
        return {
                   'id': student.id,
                   'name': student.name,
                   'email': student.email,
                   'phone': student.phone
               }, HTTPStatus.OK


def calculate_grade_point(grade):
    if grade >= 90:
        return 4.0
    elif grade >= 85:
        return 3.7
    elif grade >= 80:
        return 3.3
    elif grade >= 75:
        return 3.0
    elif grade >= 70:
        return 2.7
    elif grade >= 65:
        return 2.3
    elif grade >= 60:
        return 2.0
    elif grade >= 55:
        return 1.7
    elif grade >= 50:
        return 1.3
    elif grade >= 45:
        return 1.0
    else:
        return 0.0
