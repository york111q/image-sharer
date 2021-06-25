from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import MyUser, AccountTier, UserImage, ImageURL


# Register your models here.
admin.site.register(AccountTier)
admin.site.register(UserImage)
admin.site.register(ImageURL)


class MyUserAdmin(UserAdmin):
    list_display = ('username', 'account_type', 'is_admin')
    search_fields = ('username', 'account_type')
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(MyUser, MyUserAdmin)
