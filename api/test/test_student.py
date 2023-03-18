import json
import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from http import HTTPStatus


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

    def test_create_new_student(self):
        payload = {
            'name': 'clack',
            'email': 'clack@gmail.com',
            'phone': '123-456-7890'
        }

        response = self.client.post('/student/new_student', json=payload)

        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(response.content_type, 'application/json')

        data = json.loads(response.data)

        self.assertIn('id', data)
        self.assertIsInstance(data['id'], int)

        self.assertEqual(data['name'], payload['name'])
        self.assertEqual(data['email'], payload['email'])
        self.assertEqual(data['phone'], payload['phone'])

    def test_update_student(self):
        data = {
            'id': 1,
            'name': 'clack',
            'email': 'clack@gmail.com',
            'phone': '123-456-7890'
        }
        response = self.client.post('/student/new_student', json=data)
        data = json.loads(response.data)
        student_id = ['id']
        update_data = {
            'name': 'clack-updated',
            'email': 'clack-updated@gmail.com',
            'phone': '111-222-3333'
        }
        update_response = self.client.put(f'/student/{student_id}', json=update_data)

        self.assertEqual(update_response.status_code, HTTPStatus.OK)
        self.assertEqual(update_response.content_type, 'application/json')

        updated_data = json.loads(update_response.data)

        self.assertEqual(updated_data['id'], student_id)
        self.assertEqual(updated_data['name'], update_data['name'])
        self.assertEqual(updated_data['email'], update_data['email'])
        self.assertEqual(updated_data['phone'], update_data['phone'])

    def test_delete_student(self):
        payload = {
            'name': 'clack',
            'email': 'clack@gmail.com',
            'phone': '123-456-7890'
        }
        response = self.client.post('/student/new_student', json=payload)
        data = json.loads(response.data)
        student_id = data['id']

        delete_response = self.client.delete(f'/student/{student_id}')

        self.assertEqual(delete_response.status_code, HTTPStatus.NO_CONTENT)
        self.assertEqual(delete_response.data, b'')

        get_response = self.client.get(f'/student/{student_id}')

        self.assertEqual(get_response.status_code, HTTPStatus.NOT_FOUND)
