from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from shop.models import Contact
from shop.serializers import ContactSerializer
from rest_framework.response import Response

class ContactListView(APIView):
    """
    Получение списка всех контактов текущего пользователя.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """
        Возвращает список контактов пользователя.
        """
        contacts = Contact.objects.filter(user=request.user)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)


class ContactCreateView(APIView):
    """
    Создание нового контактного адреса.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """
        Ожидает данные для создания контакта:
        - city, street, house, structure, building, apartment, phone

        Привязывает контакт к текущему пользователю.
        """
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactDeleteView(APIView):
    """
    Удаление контактного адреса пользователя по его ID.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, pk: int) -> Response:
        """
        Удаляет контакт, если он принадлежит текущему пользователю.

        :param pk: первичный ключ контакта
        """
        try:
            contact = Contact.objects.get(pk=pk, user=request.user)
        except Contact.DoesNotExist:
            return Response({'error': 'Not found or forbidden'}, status=status.HTTP_404_NOT_FOUND)

        contact.delete()
        return Response({'status': 'deleted'}, status=status.HTTP_204_NO_CONTENT)
