from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Автоматически создаёт токен для нового пользователя после регистрации.

    :param sender: Модель, отправившая сигнал (обычно User)
    :param instance: Экземпляр созданного объекта пользователя
    :param created: Флаг, указывающий, был ли объект только что создан
    :param kwargs: Прочие параметры
    """
    if created:
        Token.objects.get_or_create(user=instance)
