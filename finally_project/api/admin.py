from django.contrib import admin
from api.models import Task, Evaluation, Meeting, MeetingParticipation


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    pass


class MeetingParticipationInline(admin.TabularInline):
    list_display = ['participant',]
    model = MeetingParticipation
    extra = 1


@admin.register(Meeting)
class CallAdmin(admin.ModelAdmin):
    list_display = ['start_time', 'get_participants']
    inlines = [MeetingParticipationInline]

    
    def get_participants(self, obj):
        return ", ".join([p.email for p in obj.participants.all()])
    get_participants.short_description = 'MyUser'