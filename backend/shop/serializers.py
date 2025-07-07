from rest_framework import serializers
from django.contrib.auth import authenticate
from shop.models import (User, ProductInfo, Product, Shop, ProductParameter, Parameter, Order,
                         OrderItem, Contact, Order, OrderItem, ProductInfo)


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователя.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'type', 'company', 'position']

    def create(self, validated_data: dict) -> User:
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """
    Сериализатор для авторизации пользователя.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data: dict) -> User:
        user = authenticate(email=data['email'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials or inactive user")

class ProductParameterSerializer(serializers.ModelSerializer):
    """
    Параметры товара.
    """
    name = serializers.CharField(source='parameter.name')

    class Meta:
        model = ProductParameter
        fields = ['name', 'value']


class ProductInfoSerializer(serializers.ModelSerializer):
    """
    Информация о товаре, включая параметры.
    """
    product = serializers.CharField(source='product.name')
    shop = serializers.CharField(source='shop.name')
    parameters = ProductParameterSerializer(source='product_parameters', many=True)

    class Meta:
        model = ProductInfo
        fields = ['id', 'product', 'model', 'shop', 'price', 'price_rrc', 'quantity', 'parameters']

class CartItemSerializer(serializers.ModelSerializer):
    """
    Товары в корзине.
    """
    product = serializers.CharField(source='product_info.product.name')
    shop = serializers.CharField(source='product_info.shop.name')
    price = serializers.IntegerField(source='product_info.price')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'shop', 'price', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    """
    Корзина с позициями.
    """
    ordered_items = CartItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'state', 'ordered_items']


class AdvertisementUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления объявления (цены и описания).
    """
    class Meta:
        model = ProductInfo
        fields = ['price', 'description']

class ContactSerializer(serializers.ModelSerializer):
    """
    Контактная информация пользователя.
    """
    class Meta:
        model = Contact
        fields = ['id', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'phone']


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Позиция в заказе.
    """
    product = serializers.CharField(source='product_info.product.name')
    shop = serializers.CharField(source='product_info.shop.name')
    price = serializers.IntegerField(source='product_info.price')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'shop', 'price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    """
    Заказ пользователя, включая позиции и общую сумму.
    """
    ordered_items = OrderItemSerializer(many=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'state', 'dt', 'ordered_items', 'total']

    def get_total(self, obj: Order) -> int:
        return sum(item.product_info.price * item.quantity for item in obj.ordered_items.all())
