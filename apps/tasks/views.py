from rest_framework import viewsets
from django.contrib.auth.models import User
from rest_framework.serializers import Serializer

from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .models import Task
from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework.decorators import action


class TasksViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    search_fields = ['title']
    filter_backends = (filters.SearchFilter,)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(created_by=user, assigned_by=user)

    # def get_queryset(self):
    #     return Task.objects.filter(user=self.request.user)

    @action(methods=['GET'], detail=False, serializer_class=TaskSerializer)
    def my_tasks(self, request, *args, **kwargs):
        queryset = Task.objects.filter(assigned_by=self.request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, serializer_class=TaskSerializer)
    def completed_tasks(self, request, *args, **kwargs):
        queryset = Task.objects.filter(completed=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, serializer_class=TaskAndCommentsSerializer)
    def comments(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = TaskAndCommentsSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True, serializer_class=ChangeUserSerializer)
    def change_user(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        new_user = User.objects.get(id=self.request.data['user_id'])
        new_user.email_user(
            subject='Task Manager',
            message='New task was assigned to you',
        )
        serializer.save(assigned_by=new_user)
        return Response(serializer.data)

    @action(methods=['PATCH'], detail=True, serializer_class=Serializer)
    def complete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.completed = True
        instance.save()
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, serializer_class=CommentSerializer)
    def create_comment(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task.assigned_by.email_user(
            subject='Task Manager',
            message='Your task was commented',
        )

        if task.completed is True:
            task.assigned_by.email_user(
                subject='Task Manager',
                message='This task is completed',
            )

        serializer.save(task=task)
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
