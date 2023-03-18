import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from werkzeug.security import generate_password_hash
from ..models.user import User
from http import HTTPStatus


class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config=config_dict['testing'])

        self.appctx = self.app.app_context()
        self.appctx.push()
        self.client = self.app.test_client()

        db.create_all()

    def tearDown(self):
        db.drop_all()

        self.appctx.pop()
        self.app = None
        self.client = None

    def test_signup(self):
        data = {
            'username': "teacher",
            'email': "teacher@gmail.com",
            'password': "password"
        }

        response = self.client.post('/auth/signup', json=data)

        user = User.query.filter_by(email="teacher@gmail.com").first()

        assert user.username == "teacher"

        assert response.status_code == 201

    def test_login(self):
        data = {
            "email": "teacher@gmail.com",
            "password": "password"
        }
        response = self.client.post('/auth/login', json=data)

        assert response.status_code == 200
