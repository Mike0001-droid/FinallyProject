from django.db import models
from account.models import MyUser
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator


STATUS_CHOICES = (
    ("Открыто", "Открыто"), 
    ("В работе", "В работе"), 
    ("Выполнено", "Выполнено"),
) 

class Task(models.Model):
    name = models.CharField("Название задачи", max_length=100)
    description = models.TextField("Описание задачи", max_length=500)
    executor = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='user')
    deadline = models.DateField("Дата регистрации")
    comments = models.TextField("Комментарии", max_length=500)
    status = models.CharField("Статус", choices=STATUS_CHOICES, max_length=9, default='Открыто')

    def __str__(self):
        return f"{self.executor.last_name} - {self.name}"
    

class Evaluation(models.Model):
    evaluator = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='evaluator')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='evaluation_task')
    mark = models.IntegerField('Оценка', validators=[MaxValueValidator(5), MinValueValidator(1)])

    def __str__(self):
        return f"{self.task} - {self.mark}"
    