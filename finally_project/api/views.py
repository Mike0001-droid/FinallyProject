from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from api.serializers import TaskSerializer
from api.models import Task


class TaskViewSet(GenericViewSet):
    queryset = Task
    serializer_class = TaskSerializer

    def list(self, request):
        queryset = self.get_queryset().objects.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 
    
    def retrieve(self, request, pk):
        queryset = self.get_queryset()
        model_file = get_object_or_404(queryset, id=pk)
        serializer = self.get_serializer(model_file)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



