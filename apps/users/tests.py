from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase


class AccountTests(APITestCase):
    def test_user_register(self):
        data = {
            "first_name": "string1",
            "last_name": "string1",
            "email": "example1@gmail.com",
            "password": "string12345"
        }

        response = self.client.post('/users/register/', data, format='json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        data = {
            "first_name": "string1",
            "last_name": "string1",
            "email": "example1@gmail.com",
            "password": "string12345"
        }

        response = self.client.post('/users/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_create_access_token(self):
        """Create a user"""

        email = "string@mail.ru"
        password = "string12345"
        self.user = User.objects.create_user(email, email, password)
        jwt_fetch_data = {
            'username': email,
            'password': password
        }

        response = self.client.post('/users/token/', jwt_fetch_data, 'json')

        """Test access token"""

        token = response.json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        """Test refresh token"""

        self.refresh_token = response.json()["refresh"]

        data = {
            'refresh': self.refresh_token
        }
        response = self.client.post('/users/token/refresh/', data, 'json')
        access_token = response.json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    def test_get_all_users(self):
        response = self.client.get('/users/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
