from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from shop.serializers import RegisterSerializer, LoginSerializer
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.request import Request

class RegisterView(APIView):
    """
    Регистрация нового пользователя.

    При успешной регистрации создаётся токен и отправляется письмо на указанный email.
    """
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)

            # Отправка уведомления на email
            send_mail(
                subject='Добро пожаловать!',
                message='Вы успешно зарегистрировались на нашем сервисе. Спасибо, что выбрали нас!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Авторизация пользователя по email и паролю.

    Возвращает токен доступа.
    """
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)