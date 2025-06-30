from rest_framework import serializers
from django.contrib.auth import authenticate
from shop.models import (User, ProductInfo, Product, Shop, ProductParameter, Parameter, Order,
                         OrderItem, Contact, Order, OrderItem, ProductInfo)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'type', 'company', 'position']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials or inactive user")

class ProductParameterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='parameter.name')

    class Meta:
        model = ProductParameter
        fields = ['name', 'value']


class ProductInfoSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='product.name')
    shop = serializers.CharField(source='shop.name')
    parameters = ProductParameterSerializer(source='product_parameters', many=True)

    class Meta:
        model = ProductInfo
        fields = ['id', 'product', 'model', 'shop', 'price', 'price_rrc', 'quantity', 'parameters']

class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='product_info.product.name')
    shop = serializers.CharField(source='product_info.shop.name')
    price = serializers.IntegerField(source='product_info.price')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'shop', 'price', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    ordered_items = CartItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'state', 'ordered_items']


class AdvertisementUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInfo
        fields = ['price', 'description']

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'phone']


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='product_info.product.name')
    shop = serializers.CharField(source='product_info.shop.name')
    price = serializers.IntegerField(source='product_info.price')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'shop', 'price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemSerializer(many=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'state', 'dt', 'ordered_items', 'total']

    def get_total(self, obj):
        return sum(item.product_info.price * item.quantity for item in obj.ordered_items.all())
