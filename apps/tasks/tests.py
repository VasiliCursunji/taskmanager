import time
from datetime import timedelta

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tasks.models import Task, Comment, Timelog, Timer


class TaskTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create(username='string@mail.ru', email="string@mail.ru", password="string12345")

        # second user to test changing users / id=2
        User.objects.create(username='string2@mail.ru', email="string2@mail.ru", password="string123456798")

        # auth
        refresh = RefreshToken.for_user(self.user)
        self.client.force_authenticate(user=self.user, token=f'Bearer {refresh.access_token}')

        # creating test objects in db
        task = Task.objects.create(
            title='str',
            description='str',
            completed=True,
            created_by=self.user,
            assigned_by=self.user
        )
        Comment.objects.create(
            text='text',
            task=task
        )
        Timelog.objects.create(
            task=task,
            user=self.user,
            started_at=timezone.now(),
            duration=timedelta(100)
        )
        Timer.objects.create(
            task=task,
            user=self.user
        )
        for i in range(5):
            Task.objects.create(title=f'str{i}', description=f'str{i}', completed=False,
                                created_by=self.user, assigned_by=self.user)

    def test_create_task(self):
        data = {
            "title": "string",
            "description": "string",
            "completed": False
        }
        response = self.client.post('/tasks/tasks/', data, 'json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_get_tasks(self):
        response = self.client.get('/tasks/tasks/')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_my_tasks(self):
        response = self.client.get('/tasks/tasks/my-tasks/')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_completed(self):
        response = self.client.get('/tasks/tasks/completed-tasks/')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_create_comment(self):
        data = {
            "text": "test comment"
        }

        response = self.client.post('/tasks/tasks/1/create-comment/', data, 'json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_get_comments(self):
        response = self.client.get('/tasks/tasks/1/comments/')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_complete_task(self):
        response = self.client.patch('/tasks/tasks/1/complete/')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_retrieve_task(self):
        response = self.client.get('/tasks/tasks/1/')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_put_task(self):
        data = {
            "title": "new_string",
            "description": "new_string",
            "completed": False
        }
        response = self.client.put('/tasks/tasks/1/', data, 'json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_patch_task(self):
        data = {
            "title": "new_string123"
        }
        response = self.client.patch('/tasks/tasks/1/', data, 'json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_delete_task(self):
        response = self.client.delete('/tasks/tasks/1/')
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_change_user(self):
        data = {
            "user_id": 2
        }
        response = self.client.post('/tasks/tasks/2/change-user/', data, 'json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_amount_by_last_month(self):
        response = self.client.get('/tasks/tasks/amount-by-last-month/')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_top_by_last_month(self):
        response = self.client.get('/tasks/tasks/top-by-last-month/')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_manual_timelog(self):
        data = {
            "started_at": timezone.now(),
            "duration": "1:00:00"
        }
        response = self.client.post('/tasks/tasks/1/manual-timelog/', data, 'json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_timelog_history(self):
        response = self.client.get('/tasks/tasks/1/timelog-history/')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_timelog(self):
        response = self.client.post('/tasks/tasks/1/start-task/')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        time.sleep(1)

        response = self.client.post('/tasks/tasks/1/pause-task/')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        time.sleep(1)

        response = self.client.post('/tasks/tasks/1/stop-task/')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
