from rest_framework.serializers import ModelSerializer
from api.models import Task, Evaluation, Meeting
from rest_framework import serializers
from django.contrib.auth.models import Group


class MeetingSerializer(ModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'


class EvaluationSerializer(ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'


class TaskSerializer(ModelSerializer):
    evaluation_task = EvaluationSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = (
            'id', 'name', 'description', 'deadline', 
            'comments', 'status', 'evaluation_task',
        )


class PeriodSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    user_id = serializers.IntegerField(required=True)

    class Meta:
        model = Evaluation
        fields = ('start_date', 'end_date', 'user_id')


class GroupSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    user_id = serializers.CharField(required=False)

    class Meta:
        model = Group
        fields = ('name', 'user_id')