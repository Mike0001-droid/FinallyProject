from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from account.models import MyUser


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Пароль ещё раз', widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ('email',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label='Пароль',
        help_text='Пароли не хранятся в открытом виде, поэтому нет возможности увидеть пароль этого пользователя, '
                  'но вы можете изменить пароль, воспользовавшись '
                  '<a href="{}">этой формой</a>.',
    )

    class Meta:
        model = MyUser
        fields = ('email', 'password', 'is_superuser')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        password = self.fields.get('password')
        if password:
            password.help_text = password.help_text.format('../password/')
        user_permissions = self.fields.get('user_permissions')
        if user_permissions:
            user_permissions.queryset = user_permissions.queryset.select_related('content_type')

