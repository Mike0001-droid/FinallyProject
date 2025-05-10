from rest_framework.serializers import ModelSerializer
from api.models import Task, Evaluation


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
