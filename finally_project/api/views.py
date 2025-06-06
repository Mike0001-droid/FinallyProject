from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from api.serializers import TaskSerializer, EvaluationSerializer, \
    MeetingSerializer, PeriodSerializer, GroupSerializer
from api.models import Task, Evaluation, Meeting, MeetingParticipation, STATUS_CHOICES
from django.shortcuts import get_object_or_404
from calendar import Calendar as SysCalendar
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from rest_framework.decorators import action
from django.db.models import Avg
from account.models import MyUser
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from django.conf import settings
from django.apps import apps
from django.forms import formset_factory
from django.shortcuts import render, redirect
from .forms import MeetingForm, ParticipationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from .forms import TaskForm

FIRST_WEEKDAY = 0 

def is_admin(user):
    return user.is_authenticated and user.is_staff

def get_group_model():
    try:
        custom_group_model = getattr(settings, 'AUTH_GROUP_MODEL', None)
        if custom_group_model:
            return apps.get_model(custom_group_model)
    except (LookupError, AttributeError):
        pass


class BaseViewSet(GenericViewSet):

    def list(self, request):
        queryset = self.get_queryset().objects.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 
    
    def retrieve(self, request, pk):
        queryset = self.get_queryset()
        model_file = get_object_or_404(queryset, pk=pk)
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
        else:
            permission_classes = [AllowAny]
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

        result = average if average else None
        return Response(
            {"average": result}, 
            status=status.HTTP_201_CREATED
        )
    

class GroupManagerViewSet(BaseViewSet):
    queryset = get_group_model()
    serializer_class = GroupSerializer
    
    @action(detail=False, methods=['post'], url_path='add-to-group')
    def add_to_group(self, request):
        
        period_serializer = self.get_serializer(data=request.data)
        period_serializer.is_valid(raise_exception=True)
        user_id = period_serializer.validated_data['user_id']
        group_name = period_serializer.validated_data['name']

        user = get_object_or_404(MyUser, pk = user_id)
            
        group = get_object_or_404(self.get_queryset(), name = group_name)
        
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
            
        group = get_object_or_404(self.get_queryset(), name=group_name)
        
        user.groups.remove(group)

        return Response(
            {"result": f"Пользователь {user.email} удален из группы {group.name}"}, 
            status=status.HTTP_201_CREATED
        )

@login_required
def calendar_view(request):
    view = request.GET.get('view', 'month')
    try:
        current_date = timezone.datetime.strptime(request.GET.get('date'), '%Y-%m-%d').date()
    except:
        current_date = timezone.now().date()
    
    if view == 'month':
        cal = SysCalendar(FIRST_WEEKDAY)
        month_days = cal.monthdatescalendar(current_date.year, current_date.month)
        
        meetings = Meeting.objects.filter(
            start_time__year=current_date.year,
            start_time__month=current_date.month
        ).order_by('start_time').prefetch_related("participants")
        
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
            
        all_participants = set()
        for meeting in meetings:
            for user in meeting.participants.all():
                all_participants.add(user)

        context = {
            'view': view,
            'all_participants': all_participants,
            'current_month': current_date,
            'month_days': month_with_meetings,
            'today': timezone.now(),
            'user': request.user,
            'is_admin': is_admin(request.user)

        }
    else:
        meetings = Meeting.objects.filter(
            start_time__date=current_date
        ).order_by('start_time').prefetch_related("participants")
        all_participants = set()
        for meeting in meetings:
            for user in meeting.participants.all():
                all_participants.add(user)

        context = {
            'view': view,
            'all_participants': all_participants,
            'current_day': current_date,
            'day_meetings': meetings,
            'previous_day': current_date - timedelta(days=1),
            'next_day': current_date + timedelta(days=1),
            'hours': range(0, 24),
            'is_admin': is_admin(request.user)

        }
    
    return render(request, 'calendar.html', context)

@login_required
@user_passes_test(is_admin)
def create_meeting(request):
    ParticipationFormSet = formset_factory(ParticipationForm, extra=1)
    
    if request.method == 'POST':
        meeting_form = MeetingForm(request.POST)
        formset = ParticipationFormSet(request.POST, prefix='participants')
        if meeting_form.is_valid() and formset.is_valid():
            meeting = meeting_form.save()
            for form in formset:
                if form.cleaned_data.get('participant'):
                    MeetingParticipation.objects.create(
                        meeting=meeting,
                        participant=form.cleaned_data['participant']
                    )
            return redirect('calendar')
    else:
        meeting_form = MeetingForm()
        formset = ParticipationFormSet(prefix='participants')
    
    return render(request, 'create.html', {
        'meeting_form': meeting_form,
        'formset': formset,
    })


@login_required
def tasks_list(request):
    if is_admin(request.user):
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(executor=request.user)
    status_filter = request.GET.get('status')
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    return render(request, 'tasks_list.html', {
        'tasks': tasks,
        'status_choices': STATUS_CHOICES,
        'is_admin': is_admin(request.user)
    })

@login_required
@user_passes_test(is_admin)
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskForm()
    
    return render(request, 'task_form.html', {
        'form': form,
        'is_admin': True
    })

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'task_detail.html', {
        'task': task,
        'is_admin': is_admin(request.user)
    })

@login_required
@user_passes_test(is_admin)
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'task_form.html', {
        'form': form,
        'is_admin': True
    })