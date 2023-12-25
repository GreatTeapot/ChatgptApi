# admin.py

from django.contrib import admin
from .models import Story, Games, ChatText


class ChatTextInline(admin.TabularInline):
    model = ChatText
    extra = 1


class GamesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'story', 'game_name', 'health', 'hunger', 'thirst')
    search_fields = ('game_name', 'user__username', 'story__name')
    inlines = [ChatTextInline]


class StoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'role', 'health', 'hunger', 'thirst')
    search_fields = ('name', 'user__username')


admin.site.register(Games, GamesAdmin)
admin.site.register(ChatText)
admin.site.register(Story, StoryAdmin)
