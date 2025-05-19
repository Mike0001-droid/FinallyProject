from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from api.serializers import TaskSerializer, EvaluationSerializer, \
    MeetingSerializer, PeriodSerializer, GroupSerializer
from api.models import Task, Evaluation, Meeting
from django.shortcuts import get_object_or_404
from calendar import Calendar
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from rest_framework.decorators import action
from django.db.models import Avg
from django.contrib.auth.models import Group
from account.models import MyUser
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated


class BaseViewSet(GenericViewSet):
    queryset = None
    serializer_class = None

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


class TaskViewSet(BaseViewSet):
    queryset = Task
    serializer_class = TaskSerializer


class EvaluationViewSet(BaseViewSet):
    queryset = Evaluation
    serializer_class = EvaluationSerializer
    
    @action(
        detail=False,
        methods=['get'],
        url_path=r'get_by_user/(?P<user_id>[^/]+)',
        url_name='get-by-user'
    )
    def get_by_user(self, request, user_id):
        queryset = self.get_queryset().objects.filter(
            task__executor=user_id
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def get_permissions(self):
        if self.action == "list":
            permission_classes = [IsAdminUser]
        elif self.action == "get_by_user":
            permission_classes = [IsAuthenticated]
        elif self.action == "create":
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class MeetingViewSet(BaseViewSet):
    queryset = Meeting
    serializer_class = MeetingSerializer


class ByPeriodViewSet(GenericViewSet):
    queryset = Evaluation
    serializer_class = PeriodSerializer

    @action(detail=False, methods=['post'], url_path='by-period')
    def get_by_period(self, request):
        
        period_serializer = self.get_serializer(data=request.data)
        period_serializer.is_valid(raise_exception=True)
        
        start_date = period_serializer.validated_data['start_date']
        end_date = period_serializer.validated_data['end_date']
        user_id = period_serializer.validated_data['user_id']

        average = self.get_queryset().objects.filter(
            task__executor=user_id,
            assessment_date__range=(start_date, end_date)
        ).aggregate(Avg('mark'))['mark__avg']

        result = average if average else "Оценок не найдено!"
        return Response(
            {"average": result}, 
            status=status.HTTP_201_CREATED
        )
    

class GroupManagerViewSet(BaseViewSet):
    queryset = Group
    serializer_class = GroupSerializer
    
    @action(detail=False, methods=['post'], url_path='add-to-group')
    def add_to_group(self, request):
        
        period_serializer = self.get_serializer(data=request.data)
        period_serializer.is_valid(raise_exception=True)
        user_id = period_serializer.validated_data['user_id']
        group_name = period_serializer.validated_data['name']

        user = get_object_or_404(MyUser, pk = user_id)
            
        group = get_object_or_404(Group, name = group_name)
        
        user.groups.add(group)

        return Response(
            {"result": f"Пользователь {user.email} добавлен в группу {group.name}"}, 
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'], url_path='delete-in-group')
    def delete_in_group(self, request):
        
        period_serializer = self.get_serializer(data=request.data)
        period_serializer.is_valid(raise_exception=True)
        user_id = period_serializer.validated_data['user_id']
        group_name = period_serializer.validated_data['name']

        user = get_object_or_404(MyUser, pk=user_id)
            
        group = get_object_or_404(Group, name=group_name)
        
        user.groups.remove(group)

        return Response(
            {"result": f"Пользователь {user.email} удален из группы {group.name}"}, 
            status=status.HTTP_201_CREATED
        )

    
def calendar_view(request):
    view = request.GET.get('view', 'month')

    try:
        current_date = timezone.datetime.strptime(request.GET.get('date'), '%Y-%m-%d').date()
    except:
        current_date = timezone.now().date()
    
    if view == 'month':
        cal = Calendar(firstweekday=0)
        month_days = cal.monthdatescalendar(current_date.year, current_date.month)
        
        meetings = Meeting.objects.filter(
            start_time__year=current_date.year,
            start_time__month=current_date.month
        ).order_by('start_time')
        
        month_with_meetings = []
        for week in month_days:
            week_with_meetings = []
            for day in week:
                day_meetings = [m for m in meetings if m.start_time.date() == day]
                week_with_meetings.append({
                    'date': day,
                    'meetings': day_meetings
                })
            month_with_meetings.append(week_with_meetings)
            
        all_participants = []
        for participant in meetings:
            for user in participant.participants.all():
                all_participants.append(user)

        context = {
            'view': view,
            'all_participants': all_participants,
            'current_month': current_date,
            'month_days': month_with_meetings,
            'today': timezone.now()
        }
    else:
        meetings = Meeting.objects.filter(
            start_time__date=current_date
        ).order_by('start_time')

        all_participants = []
        for participant in meetings:
            for user in participant.participants.all():
                all_participants.append(user)

        context = {
            'view': view,
            'all_participants': all_participants,
            'current_day': current_date,
            'day_meetings': meetings,
            'previous_day': current_date - timedelta(days=1),
            'next_day': current_date + timedelta(days=1),
            'hours': range(0, 24)
        }
    
    return render(request, 'calendar.html', context)