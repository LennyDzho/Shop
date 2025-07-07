import yaml
from yaml.loader import SafeLoader
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from shop.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class PartnerUpdate(APIView):
    """
    Поставщик загружает прайс в формате YAML (файл напрямую)
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        if request.user.type != 'shop':
            return Response({'Status': False, 'Error': 'Only for shops'}, status=status.HTTP_403_FORBIDDEN)

        yaml_file = request.FILES.get('file')
        if not yaml_file:
            return Response({'Status': False, 'Error': 'File is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = yaml.load(yaml_file, Loader=SafeLoader)
        except Exception as e:
            return Response({'Status': False, 'Error': f'YAML read error: {e}'}, status=status.HTTP_400_BAD_REQUEST)

        # Проверка ключей верхнего уровня
        required_keys = {'shop', 'categories', 'goods'}
        if not isinstance(data, dict) or not required_keys.issubset(data):
            return Response({'Status': False, 'Error': f'Missing one of required keys: {required_keys}'}, status=status.HTTP_400_BAD_REQUEST)

        # Проверка магазина
        shop_name = data.get('shop')
        if not isinstance(shop_name, str):
            return Response({'Status': False, 'Error': 'Invalid shop name'}, status=status.HTTP_400_BAD_REQUEST)

        shop, _ = Shop.objects.get_or_create(name=shop_name, user=request.user)

        # Проверка категорий
        categories = data.get('categories')
        if not isinstance(categories, list):
            return Response({'Status': False, 'Error': 'categories must be a list'}, status=status.HTTP_400_BAD_REQUEST)

        for category in categories:
            if not isinstance(category, dict) or 'id' not in category or 'name' not in category:
                return Response({'Status': False, 'Error': f'Invalid category structure: {category}'}, status=status.HTTP_400_BAD_REQUEST)

            cat_obj, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
            cat_obj.shops.add(shop)

        ProductInfo.objects.filter(shop=shop).delete()

        goods = data.get('goods')
        if not isinstance(goods, list):
            return Response({'Status': False, 'Error': 'goods must be a list'}, status=status.HTTP_400_BAD_REQUEST)

        for item in goods:
            required_fields = {'id', 'name', 'category', 'price', 'price_rrc', 'quantity', 'parameters'}
            if not isinstance(item, dict) or not required_fields.issubset(item):
                return Response({'Status': False, 'Error': f'Missing fields in product item: {item}'}, status=status.HTTP_400_BAD_REQUEST)

            product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

            try:
                product_info = ProductInfo.objects.create(
                    product=product,
                    external_id=item['id'],
                    model=item.get('model', ''),
                    price=int(item['price']),
                    price_rrc=int(item['price_rrc']),
                    quantity=int(item['quantity']),
                    shop=shop
                )
            except Exception as e:
                return Response({'Status': False, 'Error': f'Invalid product info: {e}'}, status=status.HTTP_400_BAD_REQUEST)

            parameters = item['parameters']
            if not isinstance(parameters, dict):
                return Response({'Status': False, 'Error': f'parameters must be dict in item: {item}'}, status=status.HTTP_400_BAD_REQUEST)

            for name, value in parameters.items():
                if not isinstance(name, str) or not isinstance(value, str):
                    return Response({'Status': False, 'Error': f'Invalid parameter format: {name}: {value}'}, status=status.HTTP_400_BAD_REQUEST)

                param, _ = Parameter.objects.get_or_create(name=name)
                ProductParameter.objects.create(
                    product_info=product_info,
                    parameter=param,
                    value=value
                )

        return Response({'Status': True}, status=status.HTTP_200_OK)
