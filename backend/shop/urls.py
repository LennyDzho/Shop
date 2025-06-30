from django.urls import path
# from shop.views import PartnerUpdate, RegisterView, LoginView
from shop.views.product import ProductListView, ProductDetailView
from shop.views.registration import RegisterView, LoginView
from shop.views.partner import PartnerUpdate
from shop.views.cart import CartView, CartAddView, CartRemoveView
from shop.views.contact import ContactListView, ContactCreateView, ContactDeleteView
from shop.views.order import OrderConfirmView, OrderListView, OrderDetailView
from shop.views.order import OrderStatusUpdateView
urlpatterns = [
    path('partner/update/', PartnerUpdate.as_view(), name='partner-update'),
    path('user/register/', RegisterView.as_view(), name='user-register'),
    path('user/login/', LoginView.as_view(), name='user-login'),
    path('products/<int:pk>/', ProductListView.as_view(), name='product-detail'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('cart/', CartView.as_view(), name='cart-view'),
    path('cart/add/', CartAddView.as_view(), name='cart-add'),
    path('cart/remove/', CartRemoveView.as_view(), name='cart-remove'),
    path('contacts/', ContactListView.as_view(), name='contact-list'),
    path('contacts/add/', ContactCreateView.as_view(), name='contact-add'),
    path('contacts/<int:pk>/', ContactDeleteView.as_view(), name='contact-delete'),
    path('order/confirm/', OrderConfirmView.as_view(), name='order-confirm'),
    path('order/', OrderListView.as_view(), name='order-list'),
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
]
urlpatterns += [
    path('order/<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
]