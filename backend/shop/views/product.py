from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from rest_framework.request import Request
from shop.models import ProductInfo
from shop.serializers import ProductInfoSerializer
from rest_framework.exceptions import PermissionDenied

class ProductListView(APIView):
    """
    Представление для получения списка товаров или информации об одном товаре,
    а также для редактирования и удаления товара владельцем магазина.
    """
    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_object(self, pk: int, user) -> ProductInfo | None:
        """
        Получает объект товара, проверяет, принадлежит ли он текущему пользователю.
        """
        try:
            product = ProductInfo.objects.select_related('shop').get(pk=pk)
            if product.shop.user != user:
                raise PermissionDenied("You do not have permission to modify this product.")
            return product
        except ProductInfo.DoesNotExist:
            return None

    def get(self, request: Request, pk: int = None) -> Response:
        if pk:
            try:
                product = ProductInfo.objects.select_related('product', 'shop') \
                    .prefetch_related('product_parameters__parameter').get(pk=pk)
            except ProductInfo.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = ProductInfoSerializer(product)
            return Response(serializer.data)

        # если pk не передан — обычный список с фильтрацией и пагинацией:
        products = ProductInfo.objects.select_related('product', 'shop') \
            .prefetch_related('product_parameters__parameter')

        category = request.query_params.get('category')
        shop = request.query_params.get('shop')
        price_min = request.query_params.get('price_min')
        price_max = request.query_params.get('price_max')
        name = request.query_params.get('name')

        if category:
            products = products.filter(product__category_id=category)
        if shop:
            products = products.filter(shop_id=shop)
        if price_min:
            products = products.filter(price__gte=price_min)
        if price_max:
            products = products.filter(price__lte=price_max)
        if name:
            products = products.filter(product__name__icontains=name)

        ordering = request.query_params.get('ordering')
        if ordering in ['price', '-price', 'quantity', '-quantity']:
            products = products.order_by(ordering)

        try:
            limit = int(request.query_params.get('limit', 20))
            offset = int(request.query_params.get('offset', 0))
        except ValueError:
            return Response({'error': 'limit and offset must be integers'}, status=status.HTTP_400_BAD_REQUEST)

        paginated = products[offset:offset + limit]
        serializer = ProductInfoSerializer(paginated, many=True)
        return Response({
            'count': products.count(),
            'results': serializer.data
        })

    def patch(self, request: Request, pk: int) -> Response:
        """
        Обновление информации о товаре. Только для владельца товара.
        """
        product = self.get_object(pk, request.user)
        if not product:
            return Response({'error': 'Not found or forbidden'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductInfoSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, pk: int) -> Response:
        """
        Удаление товара. Только для владельца товара.
        """
        product = self.get_object(pk, request.user)
        if not product:
            return Response({'error': 'Not found or forbidden', "request": request, "pk": pk}, status=status.HTTP_403_FORBIDDEN)

        product.delete()
        return Response({'status': 'deleted'}, status=status.HTTP_204_NO_CONTENT)


class ProductDetailView(APIView):
    """
    Отдельное представление для получения детальной информации о товаре.
    """
    permission_classes = [AllowAny]

    def get(self, request: Request, pk: int) -> Response:
        """
        Возвращает подробную информацию о товаре по ID.
        """
        try:
            product = ProductInfo.objects.select_related('product', 'shop').prefetch_related('product_parameters__parameter').get(pk=pk)
        except ProductInfo.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductInfoSerializer(product)
        return Response(serializer.data)
