from django.contrib import admin

from authapp.models import AuthTempCode, User

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Пользователи"""
    list_display = ("firstname", "lastname", "patronymic", "phone")


@admin.register(AuthTempCode)
class AuthTempCodeAdmin(admin.ModelAdmin):
    """Пользователи"""
    list_display = ("user", "temp_code")

    def has_add_permission(self, request, obj=None):
        return False

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        extra_context['show_delete'] = False
        return super().changeform_view(request, object_id, extra_context=extra_context)
