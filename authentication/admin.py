from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Organization, Member


# Register your models here
 
class CustomUserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = ['email', 'full_name', 'is_staff', 'is_active']
    search_fields = ['email', 'full_name']
    readonly_fields = ['date_joined']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('full_name',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['email'].widget.attrs['autofocus'] = True
        return form


# Register other models
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at']
    search_fields = ['name', 'created_by__email']
    list_filter = ['created_at']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'is_admin', 'joined_at']
    search_fields = ['user__email', 'organization__name']
    list_filter = ['is_admin', 'joined_at']


# Register CustomUser with custom admin
admin.site.register(CustomUser, CustomUserAdmin)
