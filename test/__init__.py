from datetime import datetime

from django.test import override_settings, TestCase
from django.utils.timezone import make_aware
from juntagrico.entity.depot import Depot
from juntagrico.entity.member import Member
from juntagrico.entity.subs import Subscription, SubscriptionPart
from juntagrico.entity.subtypes import SubscriptionProduct, SubscriptionSize, SubscriptionType


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class MagTestCase(TestCase):
    def setUp(self):
        self.set_up_member()
        self.set_up_depots()
        self.set_up_sub_types()
        self.set_up_sub()

    def assertGet(self, url, code=200, member=None):
        login_member = member or self.member
        self.client.force_login(login_member.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, code)

    def assertPost(self, url, data=None, code=200, member=None):
        login_member = member or self.member
        self.client.force_login(login_member.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, code)

    @staticmethod
    def create_member(email):
        member_data = {'first_name': 'first_name',
                       'last_name': 'last_name',
                       'email': email,
                       'addr_street': 'addr_street',
                       'addr_zipcode': 'addr_zipcode',
                       'addr_location': 'addr_location',
                       'phone': 'phone',
                       'confirmed': True,
                       }
        member = Member.objects.create(**member_data)
        member.user.set_password('12345')
        member.user.save()
        return member

    def set_up_member(self):
        """
        member
        """
        self.member = self.create_member('member@email.org')

    @staticmethod
    def admin():
        """
        admin member
        """
        admin_data = {'first_name': 'admin',
                      'last_name': 'last_name',
                      'email': 'admin@email.org',
                      'addr_street': 'addr_street',
                      'addr_zipcode': 'addr_zipcode',
                      'addr_location': 'addr_location',
                      'phone': 'phone',
                      'confirmed': True,
                      }
        admin = Member.objects.create(**admin_data)
        admin.user.set_password("123456")
        admin.user.is_staff = True
        admin.user.is_superuser = True
        admin.user.save()
        return admin

    def set_up_depots(self):
        """
        depots
        """
        depot_data = {
            'code': 'c1',
            'name': 'depot',
            'contact': self.member,
            'weekday': 1}
        self.depot = Depot.objects.create(**depot_data)
        depot_data = {
            'code': 'c2',
            'name': 'depot2',
            'contact': self.member,
            'weekday': 1}
        self.depot2 = Depot.objects.create(**depot_data)

    def set_up_sub_types(self):
        """
        subscription product, size and types
        """
        sub_product_data = {
            'name': 'product'
        }
        self.sub_product = SubscriptionProduct.objects.create(**sub_product_data)
        sub_size_data = {
            'name': 'sub_name',
            'long_name': 'sub_long_name',
            'units': 1,
            'visible': True,
            'depot_list': True,
            'product': self.sub_product,
            'description': 'sub_desc'
        }
        self.sub_size = SubscriptionSize.objects.create(**sub_size_data)
        sub_type_data = {
            'name': 'sub_type_name',
            'long_name': 'sub_type_long_name',
            'size': self.sub_size,
            'shares': 1,
            'visible': True,
            'required_assignments': 10,
            'price': 1000,
            'description': 'sub_type_desc'}
        self.sub_type = SubscriptionType.objects.create(**sub_type_data)
        sub_type_data = {
            'name': 'sub_type_name2',
            'long_name': 'sub_type_long_name',
            'size': self.sub_size,
            'shares': 2,
            'visible': True,
            'required_assignments': 10,
            'price': 1000,
            'description': 'sub_type_desc'}
        self.sub_type2 = SubscriptionType.objects.create(**sub_type_data)

    def set_up_sub(self):
        """
        subscription
        """
        sub_data = {'depot': self.depot,
                    'future_depot': None,
                    'activation_date': make_aware(datetime(2017, 3, 27)).date(),
                    'deactivation_date': None,
                    'creation_date': '2017-03-27',
                    'start_date': '2018-01-01',
                    }
        self.sub = Subscription.objects.create(**sub_data)
        self.member.join_subscription(self.sub)
        self.sub.primary_member = self.member
        self.sub.save()
        SubscriptionPart.objects.create(subscription=self.sub, type=self.sub_type)
