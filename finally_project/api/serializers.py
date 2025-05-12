from rest_framework.serializers import ModelSerializer
from api.models import Task, Evaluation, Meeting
from rest_framework import serializers
from django.contrib.auth.models import Group


class MeetingSerializer(ModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'


class EvaluationSerializer(ModelSerializer):
    task_name = serializers.CharField(source='task.name', read_only=True)
    evaluator_email = serializers.CharField(source='evaluator.email', read_only=True)
    
    class Meta:
        model = Evaluation
        fields = '__all__'
        extra_kwargs = {
            'task': {'write_only': True},
            'evaluator': {'write_only': True},
        }


class TaskSerializer(ModelSerializer):
    mark = serializers.IntegerField(source='evaluation_task.mark')

    class Meta:
        model = Task
        fields = (
            'id', 'name', 'description', 'deadline', 
            'comments', 'status', 'mark',
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