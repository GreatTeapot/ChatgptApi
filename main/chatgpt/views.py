from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .models import ChatText, Story, Games
from openai import OpenAI
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ChatGptSerializer, StorySerializer, ChatTextInfo

client = OpenAI(
    api_key="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",
)
# sadas


class ChatTextList(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = ChatText.objects.all()
    serializer_class = ChatTextInfo


class ChatMasterView(APIView):
    serializer_class = ChatGptSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        game_id = kwargs.get('game_id')

        try:
            current_game = Games.objects.get(id=game_id, user=user)
            current_story = current_game.story
        except Games.DoesNotExist:
            return Response({'error': 'Invalid Game ID'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ChatGptSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.validated_data['user'] = user
        input_text = serializer.validated_data['text']
        serializer.validated_data['story'] = current_story
        serializer.validated_data['games'] = current_game

        if not Games.objects.filter(id=current_game.id, user=user, story=current_story).exists():
            return Response({'error': 'Invalid Games ID'}, status=status.HTTP_400_BAD_REQUEST)

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"В конце ты должен описать что произойдет дальше..."
                },
                {
                    "role": "assistant",
                    "content": f"  {current_story.description}."
                },
                {
                    "role": "user",
                    "content": input_text,
                }
            ],
            model="gpt-3.5-turbo-1106",
            temperature=1,
            max_tokens=1000
        )

        response_text = chat_completion.choices[0].message.content
        ChatText.objects.create(text=input_text, answer_player=response_text, story=current_story, games=current_game)

        health_indexes = [response_text.find("Здоровье - "), response_text.find("Здоровье игрока:")]
        health_values = []

        for index in health_indexes:
            if index != -1:
                value = int(response_text[index + len("Здоровье - "):].split('.')[0].strip())
                health_values.append(value)

        if health_values:
            current_story.health = max(health_values)
            current_story.save()

        response_text = response_text.replace(f"Здоровье игрока: {current_story.health}", "")
        response_data = {"text": f"{response_text} Здоровье игрока: {current_story.health}"}

        return Response(response_data, status=status.HTTP_200_OK)


class StoryView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StorySerializer

    def post(self, request, *args, **kwargs):
        # Extract the user from the authenticated token
        user = request.user

        # Add the user to the request data before validating the serializer

        request_data = request.data.copy()
        request_data['user'] = user.id
        serializer = self.serializer_class(data=request_data)

        if serializer.is_valid():
            story = serializer.save(user=user)
            Games.objects.create(user=user, story=story, game_name=f"Game for {story.name}")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, *args, **kwargs):
        # Получаем и возвращаем только те истории, которые принадлежат текущему пользователю
        user = request.user
        stories = Story.objects.filter(user=user)
        serializer = StorySerializer(stories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
