from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from shop.models import Order, Contact
from shop.serializers import OrderSerializer
from shop.utils.email import send_order_confirmation_email
from rest_framework.request import Request


class OrderConfirmView(APIView):
    """
    Подтверждает заказ пользователя, переводя его из состояния 'basket' в 'confirmed',
    присваивает контакт (адрес доставки) и отправляет email-уведомление.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        order_id = request.data.get('order_id')
        contact_id = request.data.get('contact_id')

        if not order_id or not contact_id:
            return Response({'error': 'order_id and contact_id are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            contact = Contact.objects.get(id=contact_id, user=request.user)
        except Contact.DoesNotExist:
            return Response({'error': 'Invalid contact'}, status=status.HTTP_404_NOT_FOUND)

        try:
            order = Order.objects.get(id=order_id, user=request.user, state='basket')
        except Order.DoesNotExist:
            return Response({'error': 'Basket not found'}, status=status.HTTP_404_NOT_FOUND)

        order.contact = contact
        order.state = 'confirmed'
        order.save()

        # Отправка email-подтверждения
        send_order_confirmation_email(request.user.email, order.id)

        return Response({'status': 'order confirmed and email sent'}, status=status.HTTP_200_OK)

class OrderListView(APIView):
    """
    Возвращает список заказов текущего пользователя, исключая заказы в состоянии 'basket'.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        orders = Order.objects.filter(user=request.user).exclude(state='basket')\
            .prefetch_related('ordered_items__product_info__product', 'ordered_items__product_info__shop')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetailView(APIView):
    """
    Возвращает подробную информацию о конкретном заказе пользователя по его id.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, pk: int) -> Response:
        try:
            order = Order.objects.prefetch_related('ordered_items__product_info__product', 'ordered_items__product_info__shop')\
                .get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response(serializer.data)

class OrderStatusUpdateView(APIView):
    """
    Позволяет администратору изменить статус заказа.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, pk: int) -> Response:
        # Проверка, что пользователь — администратор
        if not request.user.is_staff:
            return Response({"error": "Only admin can change order status"}, status=status.HTTP_403_FORBIDDEN)

        new_state = request.data.get("state")
        allowed_states = dict(Order._meta.get_field("state").choices).keys()

        if new_state not in allowed_states:
            return Response({"error": "Invalid state"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        order.state = new_state
        order.save()

        return Response({"status": "updated", "new_state": order.state})