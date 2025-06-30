from django.contrib.auth.models import AbstractUser
from django.db import models
from django_rest_passwordreset.tokens import get_token_generator
from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

STATE_CHOICES = (
    ('basket', 'Корзина'),
    ('new', 'Новый'),
    ('confirmed', 'Подтверждён'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменён'),
)

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),
)


class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True)
    company = models.CharField(max_length=40, blank=True)
    position = models.CharField(max_length=40, blank=True)
    type = models.CharField(choices=USER_TYPE_CHOICES, max_length=5, default='buyer')
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Shop(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField(null=True, blank=True)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    state = models.BooleanField(default=True)  # Принимает ли заказы

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=40)
    shops = models.ManyToManyField(Shop, related_name='categories', blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=80)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    model = models.CharField(max_length=80, blank=True)
    external_id = models.PositiveIntegerField()
    product = models.ForeignKey(Product, related_name='product_infos', on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, related_name='product_infos', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    price_rrc = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop', 'external_id'], name='unique_product_info')
        ]


class Parameter(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, related_name='product_parameters', on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, related_name='product_parameters', on_delete=models.CASCADE)
    value = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'], name='unique_product_parameter')
        ]


class Contact(models.Model):
    user = models.ForeignKey(User, related_name='contacts', on_delete=models.CASCADE)
    city = models.CharField(max_length=50)
    street = models.CharField(max_length=100)
    house = models.CharField(max_length=15, blank=True)
    structure = models.CharField(max_length=15, blank=True)
    building = models.CharField(max_length=15, blank=True)
    apartment = models.CharField(max_length=15, blank=True)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.city}, {self.street}, {self.house}'


class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    dt = models.DateTimeField(auto_now_add=True)
    state = models.CharField(choices=STATE_CHOICES, max_length=15, default='basket')  # <- default: корзина
    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'Order #{self.pk} ({self.state}) for {self.user.email}'



class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='ordered_items', on_delete=models.CASCADE)
    product_info = models.ForeignKey(ProductInfo, related_name='ordered_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['order', 'product_info'], name='unique_order_item')
        ]



class ConfirmEmailToken(models.Model):
    user = models.ForeignKey(User, related_name='confirm_email_tokens', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=64, unique=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = get_token_generator().generate_token()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'Token for {self.user}'
