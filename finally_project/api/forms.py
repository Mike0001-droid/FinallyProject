from django import forms
from .models import Meeting, MeetingParticipation, MyUser

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