from django.apps import AppConfig


class ShopConfig(AppConfig):
    """
    Конфигурация приложения 'shop'.
    Здесь подключаются сигналы при готовности приложения.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'

    def ready(self):
        """
        Импорт сигналов приложения при старте Django.
        """
        import shop.signals

