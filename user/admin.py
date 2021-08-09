from django.contrib import admin
from django.contrib.auth.models import User
from .models import Profile
# Register your models here.
class ProfileInline(admin.StackedInline):
	model = Profile

class UserAdmin(admin.ModelAdmin):
	inlines = (ProfileInline,)

admin.site.unregister(User)
admin.site.register(Profile)
admin.site.register(User, UserAdmin)