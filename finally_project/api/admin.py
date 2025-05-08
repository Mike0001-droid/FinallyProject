from django.contrib import admin
from api.models import Task, Evaluation


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    pass