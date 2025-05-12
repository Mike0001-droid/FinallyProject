from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import (
    AdminPasswordChangeForm
)
from account.forms import UserChangeForm, UserCreationForm
from account.models import MyUser, Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    pass


class UserAdmin(BaseUserAdmin):
    # Формы для добавления и изменения пользовательских экземпляров
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    # Поля, которые будут использоваться при отображении модели пользователя.
    # Они переопределяют определения в базовом User Admin,
    # которые ссылаются на определенные поля в auth.User.
    list_display = ('id', 'email', 'is_superuser', 'get_groups')
    list_filter = ('is_superuser', 'groups')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Permissions', {'fields': ('is_superuser', 'user_permissions', 'groups', 'team')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')})
    )
    # add_fieldsets не является стандартным атрибутом ModelAdmin. UserAdmin
    # переопределяет get_fieldsets, чтобы использовать этот атрибут при создании пользователя.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('user_permissions',)

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Группы'

admin.site.register(MyUser, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Group)
