from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import (
    AdminPasswordChangeForm
)
from account.forms import UserChangeForm, UserCreationForm
from account.models import MyUser, Team
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _

class GroupFilter(SimpleListFilter):
    title = _('Группы') 
    parameter_name = 'groups'

    def lookups(self, request, model_admin):
        from django.contrib.auth.models import Group
        groups = Group.objects.all()
        return [(group.id, group.name) for group in groups]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(groups__id=self.value())
        return queryset


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_joined')


class UserAdmin(BaseUserAdmin):
    # Формы для добавления и изменения пользовательских экземпляров
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    # Поля, которые будут использоваться при отображении модели пользователя.
    # Они переопределяют определения в базовом User Admin,
    # которые ссылаются на определенные поля в auth.User.
    list_display = ('id', 'email', 'is_superuser', 'get_groups')
    list_filter = ('is_superuser', GroupFilter)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Permissions', {'fields': ('is_superuser', 'user_permissions', 'groups')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
        ('Организация', {'fields': ('team',)})
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
    filter_horizontal = ('user_permissions', 'groups')

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Группы'

admin.site.register(MyUser, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Group)
