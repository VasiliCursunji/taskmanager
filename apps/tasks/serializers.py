from rest_framework import serializers
from .models import Task, Comment, TimeLog


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {
            'created_by': {'read_only': True},
            'assigned_by': {'read_only': True}
        }


class ChangeUserSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = Task
        fields = (
            'user_id',
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
        model = TimeLog
        fields = ()
        extra_kwargs = {
            'task': {'read_only': True},
        }