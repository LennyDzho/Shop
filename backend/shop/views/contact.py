from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from shop.models import Contact
from shop.serializers import ContactSerializer


class ContactListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        contacts = Contact.objects.filter(user=request.user)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)


class ContactCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            contact = Contact.objects.get(pk=pk, user=request.user)
        except Contact.DoesNotExist:
            return Response({'error': 'Not found or forbidden'}, status=status.HTTP_404_NOT_FOUND)

        contact.delete()
        return Response({'status': 'deleted'}, status=status.HTTP_204_NO_CONTENT)
