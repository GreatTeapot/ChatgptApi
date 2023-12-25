from rest_framework.generics import ListAPIView
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


class ChatTextListByGameView(ListAPIView):
    """
        Принимает access token и по id {game_id} и выводит все истории общение с chatgpt которые хранятся в  определенном Games
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChatTextInfo

    def get_queryset(self):

        user = self.request.user
        game_id = self.kwargs.get('game_id')

        try:
            current_game = Games.objects.get(id=game_id, user=user)
        except Games.DoesNotExist:
            return ChatText.objects.none()

        # Возвращаем все объекты ChatText для данной игры и пользователя
        return ChatText.objects.filter(games=current_game)


class ChatTextView(APIView):
    """
        Принимает access token и по id {game_id} апи выбирает игру и по  {chat_text_id} он выбирает определенную историю по его id
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChatTextInfo

    def get(self, request, *args, **kwargs):

        game_id = kwargs.get('game_id')
        chat_text_id = kwargs.get('chat_text_id')

        try:
            current_game = Games.objects.get(id=game_id, user=request.user)
            chat_text = ChatText.objects.get(id=chat_text_id, games=current_game)
            serializer = ChatTextInfo(chat_text)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Games.DoesNotExist:
            return Response({'error': 'Invalid Game ID'}, status=status.HTTP_400_BAD_REQUEST)
        except ChatText.DoesNotExist:
            return Response({'error': 'Invalid ChatText ID'}, status=status.HTTP_400_BAD_REQUEST)


class AllGames(generics.ListAPIView):
    """
    Принимает access token и выводит все Игровые тексты которые хранятся в модельке Games
    """
    permission_classes = [AllowAny]
    queryset = ChatText.objects.all()
    serializer_class = ChatTextInfo


class ChatMasterView(APIView):
    """
    Принимает access token и по id {game_id} из апи он сохраняет текст и ответ от chatgpt в модельке Games по его id
    """
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
        serializer.validated_data['games'] = current_game

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"В зависимости от хороших и плохих ситуаций игрок может потерять или повысить характеристики у персонажа есть харатеристики Здоровье, Голод, Жажда которые по умолчанию равны 100 в конце ответа выводи результаты характеристик и чтобы каждая характеристика было с новым обзацем вот характеристики: "
                               f"Здоровье:{current_story.health}"
                               f"Голод:{current_story.hunger}"
                               f"Жажда:{current_story.thirst}"
                               f"Также выводи в конце что Ваша роль:{current_story.role}"
                },
                {
                    "role": "user",
                    "content": serializer.validated_data['text'],
                }
            ],
            model="gpt-3.5-turbo-1106",
            temperature=1,
            max_tokens=1000
        )

        response_text = chat_completion.choices[0].message.content

        character_attributes = extract_character_attributes(response_text)
        if character_attributes:
            current_health = current_story.health
            current_hunger = current_story.hunger
            current_thirst = current_story.thirst

            current_story.health = character_attributes.get('health', current_story.health)
            current_story.hunger = character_attributes.get('hunger', current_story.hunger)
            current_story.thirst = character_attributes.get('thirst', current_story.thirst)
            current_story.save()

            current_game.health = current_story.health
            current_game.hunger = current_story.hunger
            current_game.thirst = current_story.thirst
            current_game.save()

        ChatText.objects.create(
            text=serializer.validated_data['text'],
            chatgpt_answer=response_text,
            games=current_game,
            health=character_attributes.get('health', current_health),
            hunger=character_attributes.get('hunger', current_hunger),
            thirst=character_attributes.get('thirst', current_thirst),
        )

        response_data = {
            "text": f"{response_text}"
        }

        return Response(response_data, status=status.HTTP_200_OK)


def extract_character_attributes(response_text):
    attributes = {'health': 100, 'hunger': 100, 'thirst': 100}

    if 'Здоровье:' in response_text:
        index = response_text.find('Здоровье:')
        try:
            attributes['health'] = int(response_text[index + len('Здоровье:'):].split()[0])
        except ValueError:
            pass

    if 'Голод:' in response_text:
        index = response_text.find('Голод:')
        try:
            attributes['hunger'] = int(response_text[index + len('Голод:'):].split()[0])
        except ValueError:
            pass

    if 'Жажда:' in response_text:
        index = response_text.find('Жажда:')
        try:
            attributes['thirst'] = int(response_text[index + len('Жажда:'):].split()[0])
        except ValueError:
            pass

    return attributes


class StoryView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StorySerializer

    def post(self, request, *args, **kwargs):
        """
        Принимает access token и это Апи для создание Story(характеристик игрока)
        """

        user = request.user
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
        """
        Принимает access token и выводит все Story модельки пользвателя
        """
        user = request.user
        stories = Story.objects.filter(user=user)
        serializer = StorySerializer(stories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
