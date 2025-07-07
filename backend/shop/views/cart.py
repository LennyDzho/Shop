from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from shop.models import Order, OrderItem, ProductInfo
from shop.serializers import CartSerializer
from rest_framework.request import Request
from rest_framework.response import Response

class CartView(APIView):
    """
    Получение текущей корзины пользователя. Если корзины нет — создаётся новая.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """
        Возвращает содержимое корзины текущего пользователя.
        """
        cart, _ = Order.objects.get_or_create(user=request.user, state='basket')
        cart.refresh_from_db()
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartAddView(APIView):
    """
    Добавление товара в корзину. Если товар уже есть — увеличивает количество.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """
        Ожидает поля:
        - product_info: ID ProductInfo
        - quantity: количество (по умолчанию 1)

        Создаёт новую запись или увеличивает количество.
        """
        product_info_id = request.data.get('product_info')
        quantity = int(request.data.get('quantity', 1))

        try:
            product_info = ProductInfo.objects.get(id=product_info_id)
        except ProductInfo.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        cart, _ = Order.objects.get_or_create(user=request.user, state='basket')

        try:
            item = OrderItem.objects.get(order=cart, product_info=product_info)
            item.quantity += quantity
            item.save()
        except OrderItem.DoesNotExist:
            OrderItem.objects.create(order=cart, product_info=product_info, quantity=quantity)

        return Response({'status': 'added'}, status=status.HTTP_201_CREATED)



class CartRemoveView(APIView):
    """
    Удаление позиции из корзины пользователя по item_id.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """
        Ожидает поле:
        - item_id: ID элемента корзины (OrderItem)

        Удаляет позицию из корзины, если найдена.
        """
        item_id = request.data.get('item_id')
        try:
            item = OrderItem.objects.get(id=item_id, order__user=request.user, order__state='basket')
            item.delete()
            return Response({'status': 'deleted'})
        except OrderItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
