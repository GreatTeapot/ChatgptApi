from django.urls import path
from .views import ChatMasterView, StoryView, AllGames, ChatTextView

urlpatterns = [
    path('game/<int:game_id>/game/', ChatMasterView.as_view(), name='game_master'),
    path('story/', StoryView.as_view(), name='story'),
    path('all-games/', AllGames.as_view(), name='all-games'),
    path('game/<int:game_id>/game/<int:chat_text_id>/', ChatTextView.as_view(), name='chat_text_detail'),

]
