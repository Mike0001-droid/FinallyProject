from django import forms
from .models import Meeting, MeetingParticipation, MyUser, Task

class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['start_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class ParticipationForm(forms.ModelForm):
    participant = forms.ModelChoiceField(queryset=MyUser.objects.all())
    
    class Meta:
        model = MeetingParticipation
        fields = ['participant']


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'executor', 'deadline', 'status', 'comments']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'comments': forms.Textarea(attrs={'rows': 4}),
        }