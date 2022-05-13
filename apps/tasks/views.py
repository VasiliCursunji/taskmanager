from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.serializers import Serializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.tasks.models import Task, Timelog, Timer, TaskQuerySet
from apps.tasks.serializers import TaskSerializer, TaskAndCommentsSerializer, CommentSerializer, ChangeUserSerializer, \
    ManualTimeLogSerializer, TaskTimeLogSerializer, DetailTaskSerializer


class TasksViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )
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

    def get_queryset(self):
        queryset: TaskQuerySet = super(TasksViewSet, self).get_queryset()
        if self.action == 'list':
            return queryset.with_total_duration()
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = DetailTaskSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

    @action(methods=['GET'], detail=True, serializer_class=TaskTimeLogSerializer, url_path='timelog-history')
    def timelog_history(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='amount-by-last-month')
    def amount_by_last_month(self, request, *args, **kwargs):
        amount_time = Timelog.objects.filter(
            started_at__month__gte=timezone.now().month,
            started_at__year__gte=timezone.now().year,
            user=self.request.user,
        ).aggregate(sum=Sum('duration'))

        return Response({'last_month': amount_time}, status=status.HTTP_200_OK)

    @method_decorator(cache_page(60))
    @action(methods=['GET'], detail=False, serializer_class=TaskSerializer, url_path='top-by-last-month')
    def top_by_last_month(self, request, *args, **kwargs):
        queryset = self.queryset.filter(
            timelog__started_at__month__gte=timezone.now().month,
            timelog__started_at__year__gte=timezone.now().year,
        ).annotate(total_duration=Sum('timelog__duration')
                   ).order_by('-total_duration')[:20]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['PATCH'], detail=True, serializer_class=Serializer)
    def complete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.complete()
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, serializer_class=Serializer, url_path='start-task')
    def start_task(self, request, *args, **kwargs):
        instance = Timer.objects.create(user=self.request.user, task=self.get_object())
        instance.start()

        return Response(status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True, serializer_class=Serializer, url_path='pause-task')
    def pause_task(self, request, *args, **kwargs):
        instance = Timer.objects.filter(user=self.request.user, task=self.get_object()).last()
        instance.pause()

        return Response(status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True, serializer_class=Serializer, url_path='stop-task')
    def stop_task(self, request, *args, **kwargs):
        instance = Timer.objects.filter(user=self.request.user, task=self.get_object()).last()
        instance.stop()

        return Response(instance.total_duration, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True, serializer_class=ManualTimeLogSerializer, url_path='manual-timelog')
    def manual_timelog(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task=instance, user=request.user)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, serializer_class=ChangeUserSerializer, url_path='change-user')
    def change_user(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        new_user = User.objects.get(id=self.request.data['user_id'])
        serializer.save(assigned_by=new_user)
        new_user.email_user(
            subject='Task Manager',
            message='New task was assigned to you',
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, serializer_class=CommentSerializer, url_path='create-comment')
    def create_comment(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task)
        task.assigned_by.email_user(
            subject='Task Manager',
            message='Your task was commented',
        )
        if task.completed is True:
            task.assigned_by.email_user(
                subject='Task Manager',
                message='This task is completed',
            )
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
