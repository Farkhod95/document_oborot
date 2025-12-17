from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin, GroupAdmin

from users.models import User, Role, AppModule, Company


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('fullname', 'email', 'companies')}),
        (_('Permissions'),
         {'fields': ('is_active', 'is_staff', 'roles')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('fullname', 'email', 'gender', 'is_active', 'username', 'password1',
                       'password2', 'roles', 'address', 'companies'),
        }),
    )
    list_display = ('username', 'email', 'fullname', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'roles')
    search_fields = ('username', 'fullname', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

    def is_admin(self, obj) -> bool:
        return obj.is_admin()

    is_admin.boolean = True



@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_active', 'phone', 'country', 'region', 'district', 'address')
    fields = ('code', 'name', 'is_active', 'phone', 'country', 'region', 'district', 'address', 'logo')
    search_fields = ('name', 'code', 'country', 'region', 'district',)


@admin.register(Role)
class RoleAdmin(GroupAdmin):
    list_display = ('name', 'description')
    fields = ('name', 'description', 'permissions')
    search_fields = ('name', 'description')
    filter_horizontal = ('permissions',)


@admin.register(AppModule)
class AppModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'on_dashboard')

