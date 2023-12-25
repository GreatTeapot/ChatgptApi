# chatgpt/admin.py
from django.contrib import admin
from .models import ChatText, Story, Games


class ChatTextInline(admin.TabularInline):
    model = ChatText
    extra = 1  # Количество пустых форм для добавления


class GamesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'story', 'game_name', 'max_events')
    search_fields = ('game_name', 'user__username', 'story__name')
    inlines = [ChatTextInline]  # Добавляем InlineModelAdmin для связанных ChatText


class StoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'role', 'description', 'health', 'user')
    search_fields = ('name', 'user__username')
    inlines = [ChatTextInline]


admin.site.register(Games)
admin.site.register(ChatText)
admin.site.register(Story)
