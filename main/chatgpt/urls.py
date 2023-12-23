from django.urls import path
from .views import ChatMasterView, StoryView, ChatTextList

urlpatterns = [
    path('game/<int:game_id>/game/', ChatMasterView.as_view(), name='game_master'),
    path('story/', StoryView.as_view(), name='story'),
    path('game/<int:pk>/', ChatTextList.as_view(), name='user-update'),
    path('all-games/', ChatTextList.as_view(), name='user-update'),

]
