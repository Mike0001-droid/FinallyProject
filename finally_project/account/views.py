from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
from rest_framework import status
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from finally_project import settings
from account.serializers import MyUserSerializer, MyTokenObtainPairSerializer, \
    MyTeamSerializer
from account.models import MyUser, Team
PermissionClass = IsAuthenticated if not settings.DEBUG else AllowAny

class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = MyTokenObtainPairSerializer


class MyUserViewSet(ViewSet):
    """
    list:
        Авторизированный пользователь
    create_user:
        Создание пользователя
    update_user:
        Обновление пользователей
    """

    def list(self, request):
        serializer = MyUserSerializer(request.user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def create_user(self, request):
        serializer = MyUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        else:
            text_error = ''
            error_dict = {}
            for error in serializer.errors:
                elm_error = serializer.errors.get(error)
                if len(elm_error) > 0:
                    text_error += "{} \n".format(elm_error[0])
                    error_dict.update({error: elm_error[0]})
            return Response({"detail": text_error, "error": error_dict}, status=status.HTTP_400_BAD_REQUEST)

        token_data = {
            "email": request.data["email"],
            "password": request.data["password"]
        }
        token_serializer = MyTokenObtainPairSerializer(data=token_data)
        token_serializer.is_valid(raise_exception=True)
        return Response(token_serializer.validated_data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def update_user(self, request):
        if 'email' in request.data:
            del request.data['email']
        if 'password' in request.data:
            request.data['password'] = make_password(request.data['password'])
        serializer = MyUserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def password_reset_user(self, request):
        if 'email' in request.data:
            email = request.data.get('email')
            try:
                user = MyUser.objects.get(email=email)
                password = MyUser.objects.make_random_password()
                user.set_password(password)
                user.save(update_fields=['password'])
                message = "Запрос на восстановление пароля \nНовый пароль сгенерирован: {password}".format(password=password)
                send_mail('Смена пароля', message, settings.EMAIL_HOST_USER, [email])
                return Response({'detail': 'Новый пароль отправлен на емайл: {}'.format(email)}, status=status.HTTP_200_OK)
            except MyUser.DoesNotExist:
                text = 'Пользователь с емайлом {}, не найден'.format(email)
                return Response({'detail': text, 'error': {'email': text}}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response(
                    {'detail': 'Произошла неизвестная ошибка', 'error': {'email': 'Произошла неизвестная ошибка'}},
                    status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Не передан емайл', 'error': {'email': 'Не передан емайл'}},
                        status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [IsAuthenticated]
        elif self.action == "create_user":
            permission_classes = [AllowAny]
        elif self.action == "update_user":
            permission_classes = [IsAuthenticated]
        elif self.action == "password_reset_user":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class TeamViewSet(GenericViewSet):
    queryset = Team
    serializer_class = MyTeamSerializer

    def list(self, request):
        queryset = self.get_queryset().objects.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 
    
    def retrieve(self, request, pk):
        queryset = self.get_queryset()
        model_file = get_object_or_404(queryset, id=pk)
        serializer = self.get_serializer(model_file)
        return Response(serializer.data, status=status.HTTP_200_OK)