from django.contrib import admin
from django.contrib.auth.models import User


class UserAdmin(admin.ModelAdmin):
    fields = ('username', 'email', 'password', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_superuser')
    list_display = ('pk', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_display_links = ('username',)
    search_fields = ('username',)
    list_filter = ('is_staff', 'is_active')
    actions = ('toggle_user_active_status',)
    ordering = ('pk',)
    list_per_page = 10

    @admin.action(description="Toggle users' active status")
    def toggle_user_active_status(self, request, queryset):
        for user in queryset:
            user.is_active = not user.is_active
            user.save(update_fields=['is_active'])
        self.message_user(request, 'The users status is changed.')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
