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

        shop, _ = Shop.objects.get_or_create(name=data['shop'], user=request.user)

        for category in data['categories']:
            cat_obj, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
            cat_obj.shops.add(shop)

        ProductInfo.objects.filter(shop=shop).delete()

        for item in data['goods']:
            product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

            product_info = ProductInfo.objects.create(
                product=product,
                external_id=item['id'],
                model=item.get('model', ''),
                price=item['price'],
                price_rrc=item['price_rrc'],
                quantity=item['quantity'],
                shop=shop
            )

            for name, value in item['parameters'].items():
                param, _ = Parameter.objects.get_or_create(name=name)
                ProductParameter.objects.create(
                    product_info=product_info,
                    parameter=param,
                    value=value
                )

        return Response({'Status': True}, status=status.HTTP_200_OK)