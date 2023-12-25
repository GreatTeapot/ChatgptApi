from django.urls import path
from .views import ChatMasterView, StoryView, AllGames, ChatTextView, ChatTextListByGameView

urlpatterns = [
    path('games/<int:game_id>/action/', ChatMasterView.as_view(), name='game_master'),
    path('story/', StoryView.as_view(), name='story'),
    path('all-games/', AllGames.as_view(), name='all-games'),
    path('games/<int:game_id>/action/<int:chat_text_id>/', ChatTextView.as_view(), name='chat_text_detail'),
    path('games/<int:game_id>/actions/', ChatTextListByGameView.as_view(), name='chattext-list-by-game'),

]
