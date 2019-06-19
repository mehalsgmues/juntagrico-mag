from django.apps import AppConfig

from juntagrico.util.addons import *


class MehalsgmuesAppConfig(AppConfig):
    name = 'mehalsgmues'

    def ready(self):
        user_menu = get_user_menus()
        user_menu.append('mag_user_menu.html')
        set_user_menus(user_menu)
