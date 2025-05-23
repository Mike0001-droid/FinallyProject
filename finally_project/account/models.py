from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Email is required")
        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Team(models.Model):
    name = models.CharField('Название команды', max_length=100)
    date_joined = models.DateField('Дата регистрации', default=timezone.now)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'



class MyUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='Емайл',
        max_length=255,
        unique=True,
    )
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    phone = models.CharField('Телефон', max_length=15, blank=True, default="")
    date_joined = models.DateTimeField('Дата регистрации', default=timezone.now)
    is_active = models.BooleanField('Активный', help_text='Отметьте, если пользователь должен считаться активным. '
                                                          'Уберите эту отметку вместо удаления учётной записи.', default=True)
    is_staff = models.BooleanField('Статус персонала', help_text='Отметьте, если пользователь может входить в '
                                                                 'административную часть сайта.', default=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='users', null=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

    def full_name(self):
        return f'{self.first_name} {self.last_name}' if self.first_name and self.last_name else None

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send notification to this user via email"""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ["-date_joined"]