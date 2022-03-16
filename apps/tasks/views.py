from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.serializers import Serializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.tasks.models import Task
from apps.tasks.serializers import TaskSerializer, TaskAndCommentsSerializer, CommentSerializer, ChangeUserSerializer, \
    TimeLogSerializer


class TasksViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    filter_fields = (
        'completed',
    )
    search_fields = (
        'title',
    )
    ordering_fields = (
        'id',
    )

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(created_by=user, assigned_by=user)

    @action(methods=['GET'], detail=False, serializer_class=TaskSerializer, url_path='my-tasks')
    def my_tasks(self, request, *args, **kwargs):
        queryset = self.queryset.filter(assigned_by=self.request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, serializer_class=TaskSerializer, url_path='completed-tasks')
    def completed_tasks(self, request, *args, **kwargs):
        queryset = self.queryset.filter(completed=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, serializer_class=TaskAndCommentsSerializer)
    def comments(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True, serializer_class=ChangeUserSerializer, url_path='change-user')
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
        instance.complete()
        instance.save()
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, serializer_class=TimeLogSerializer, url_path='start-task')
    def start_task(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = TimeLogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task=instance)
        return Response(status=status.HTTP_201_CREATED)

    # @action(methods=['PATCH'], detail=True, serializer_class=Serializer, url_path='pause-task')
    # def pause_task(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #
    #     instance.save()
    #     return Response(status=status.HTTP_201_CREATED)
    #
    # @action(methods=['PATCH'], detail=True, serializer_class=Serializer, url_path='stop-task')
    # def stop_task(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     instance.is_stopped = True
    #     instance.save()
    #     return Response(status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, serializer_class=CommentSerializer, url_path='create-comment')
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
