from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


class TaskTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create(username='string@mail.ru', email="string@mail.ru", password="string12345")
        refresh = RefreshToken.for_user(self.user)
        self.client.force_authenticate(user=self.user, token=f'Bearer {refresh.access_token}')
        # self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_create_task(self):
        data = {
            "title": "string",
            "description": "string",
            "completed": True
        }
        response = self.client.post('/tasks/tasks/', data, 'json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
