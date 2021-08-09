from posts.models import Post,Comment,Vote
from django.contrib import admin

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display =('body','slug','user','created')


admin.site.register(Post,PostAdmin)
admin.site.register(Comment)
admin.site.register(Vote)