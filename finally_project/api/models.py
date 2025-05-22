from django.db import models
from account.models import MyUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone


STATUS_CHOICES = (
    ("Открыто", "Открыто"), 
    ("В работе", "В работе"), 
    ("Выполнено", "Выполнено"),
) 

class Task(models.Model):

    class StatusChoices(models.TextChoices):
        OPEN = 'Открыто'
        IN_PROCESS = 'В работе'
        COMPLETED = 'Выпоолнено'

    name = models.CharField("Название задачи", max_length=150)
    description = models.TextField("Описание задачи", max_length=500)
    executor = models.ForeignKey(
        MyUser, on_delete=models.CASCADE, 
        related_name='tasks_as_executor', 
        verbose_name='Исполнитель'
    )
    deadline = models.DateField("Дедлайн")
    comments = models.TextField("Комментарии", max_length=500, null=True, blank=True)
    status = models.CharField("Статус", choices=StatusChoices, default='Открыто')

    def __str__(self):
        return f"{self.name} ({self.executor.email})"
    
    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
    

class Evaluation(models.Model):
    evaluator = models.ForeignKey(
        MyUser, on_delete=models.CASCADE, 
        related_name='evaluations_given', verbose_name="Оценщик"
    )
    task = models.OneToOneField(
        Task, on_delete=models.CASCADE, 
        verbose_name="Задача"
    )
    mark = models.IntegerField('Оценка', validators=[MaxValueValidator(5), MinValueValidator(1)])
    assessment_date = models.DateField('Дата оценивания', default=timezone.now)

    def __str__(self):
        return f"{self.task} - {self.mark}"
    
    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'


class Meeting(models.Model):
    start_time = models.DateTimeField("Начало встречи")
    participants = models.ManyToManyField(
        MyUser, through='MeetingParticipation', 
        verbose_name="Участники"
    )
    
    class Meta:
        verbose_name = 'Встреча'
        verbose_name_plural = 'Встречи'


class MeetingParticipation(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    participant = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    start_time = models.DateTimeField(editable=False, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['participant', 'start_time'],
                violation_error_message="Участник уже записан на встречу в это время!",
                name='unique_participant_per_time'
            )
        ]

    def save(self, *args, **kwargs):
        if not self.start_time:
            self.start_time = self.meeting.start_time
        super().save(*args, **kwargs)
        