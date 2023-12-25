# chatgpt/serializers.py
from rest_framework import serializers
from authapp.models import CustomUser

from .models import ChatText, Story, Games


class ChatTextInfo(serializers.ModelSerializer):
    class Meta:
        model = ChatText
        fields = '__all__'


class GamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Games
        fields = ['id', 'user', 'story', 'game_name', 'max_events']


class ChatGptSerializer(serializers.ModelSerializer):
    games = GamesSerializer(required=False)

    class Meta:
        model = ChatText
        fields = ['id', 'text', 'chatgpt_answer',  'games']

    def create(self, validated_data):
        user = self.context['request'].user

        try:
            game_id = self.context['view'].kwargs['game_id']
            current_game = Games.objects.get(id=game_id, user=user)
        except (KeyError, Games.DoesNotExist):
            raise serializers.ValidationError({'error': 'Invalid Game ID'})

        validated_data['user'] = user
        validated_data['games'] = current_game

        chat_text = ChatText.objects.create(**validated_data)
        return chat_text


class StorySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Story
        fields = ['id', 'name', 'role', 'health', 'hunger', 'thirst', 'user']
