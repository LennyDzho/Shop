from django.core.mail import send_mail
from django.conf import settings


def send_order_confirmation_email(user_email: str, order_id: int) -> None:
    """
    Отправляет email-подтверждение пользователю о принятии заказа.

    :param user_email: Email пользователя
    :param order_id: Идентификатор заказа
    """
    subject = f'Ваш заказ №{order_id} подтвержден'
    message = f'Спасибо за заказ! Ваш заказ №{order_id} был успешно подтвержден и скоро будет обработан.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)
