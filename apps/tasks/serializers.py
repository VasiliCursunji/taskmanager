from rest_framework import serializers
from .models import Task, Comment, Timelog


class TaskSerializer(serializers.ModelSerializer):
    total_duration = serializers.DurationField()

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'description',
            'total_duration',
        )
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
