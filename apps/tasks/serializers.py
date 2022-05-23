from rest_framework import serializers

from apps.tasks.models import Task, Comment, Timelog
from apps.users.serializers import UserSerializer


class TaskSerializer(serializers.ModelSerializer):
    total_duration = serializers.DurationField(read_only=True)
    created_by = UserSerializer(read_only=True)
    assigned_by = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'description',
            'completed',
            'total_duration',
            'created_by',
            'assigned_by',
        )


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            'id',
            'text',
        )
        extra_kwargs = {
            'task': {'read_only': True},
        }


class DetailTaskSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    created_by = UserSerializer(read_only=True)
    assigned_by = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'description',
            'created_by',
            'assigned_by',
            'comments',
        )


class ChangeUserSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = Task
        fields = (
            'user_id',
        )


class TaskAndCommentsSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)

    class Meta:
        model = Task
        fields = (
            'title',
            'comments',
        )


class TimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timelog
        fields = '__all__'


class TaskTimeLogSerializer(serializers.ModelSerializer):
    timelog = TimeLogSerializer(read_only=True, many=True)

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'timelog',
        )


class ManualTimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timelog
        fields = '__all__'
        extra_kwargs = {
            'task': {'read_only': True},
            'user': {'read_only': True},
        }
