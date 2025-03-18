
from django.contrib import admin
from .models import Team,  Fixture, Player, News

admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Fixture)
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('created_at',)