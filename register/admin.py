from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy 

admin.site.site_title = gettext_lazy("Library-O Admin")
admin.site.site_header = gettext_lazy("Library-O Adminisztrátor Felület") 
admin.site.index_title = gettext_lazy("")  

admin.site.unregister(User) 

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_per_page = 20
    list_display = ('get_user', 'get_email', 'get_name', 'get_staff_status')
    search_fields = ['username']

    def get_user(self, obj):
        return obj.username
    get_user.short_description = "Felhasználó"

    def get_email(self, obj):
        return obj.email
    get_email.short_description = "E-mail cím"

    def get_name(self, obj):
        return obj.last_name + " " + obj.first_name 
    get_name.short_description = "Teljes név"

    def get_staff_status(self, obj):
        return obj.is_staff
    get_staff_status.short_description = "Alkalmazott"

       # felhasznalok tab admin panel --> átírt verzió.
    def get_model_perms(self, request):
        permission = super().get_model_perms(request)
        
        User._meta.verbose_name = gettext_lazy ("Felhasználó")
        User._meta.verbose_name_plural = gettext_lazy ("Felhasználók")
        Group._meta.verbose_name = gettext_lazy ("Csoport")
        Group._meta.verbose_name_plural = gettext_lazy ("Csoportok")
        
        User._meta.app_config.verbose_name = gettext_lazy ("Felhasználók Információ")
        
        return permission

