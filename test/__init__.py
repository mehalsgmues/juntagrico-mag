from django.test import TestCase, override_settings
from django.utils import timezone
from django.core import mail

from juntagrico.entity.depot import Depot
from juntagrico.entity.jobs import JobType, RecuringJob, OneTimeJob, Assignment, ActivityArea
from juntagrico.entity.location import Location
from juntagrico.entity.member import Member
from juntagrico.entity.subs import Subscription, SubscriptionPart
from juntagrico.entity.subtypes import SubscriptionProduct, SubscriptionSize, SubscriptionType


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class MagTestCase(TestCase):
    def setUp(self):
        self.set_up_member()
        self.set_up_admin()
        self.set_up_location()
        self.set_up_depots()
        self.set_up_sub_types()
        self.set_up_sub()
        self.set_up_area()
        self.set_up_job()
        mail.outbox.clear()

    @staticmethod
    def create_member(email):
        member_data = {'first_name': 'first_name',
                       'last_name': 'last_name',
                       'email': email,
                       'addr_street': 'addr_street',
                       'addr_zipcode': 'addr_zipcode',
                       'addr_location': 'addr_location',
                       'phone': 'phone',
                       'mobile_phone': 'phone',
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
        self.member = self.create_member('email1@email.org')

    def set_up_admin(self):
        """
        admin members
        """
        self.admin = self.create_member('admin@email.org')
        self.admin.user.set_password("123456")
        self.admin.user.is_staff = True
        self.admin.user.is_superuser = True
        self.admin.user.save()

    def set_up_location(self):
        """
        location
        """
        location_data_depot = {'name': 'Depot location',
                               'latitude': '12.513',
                               'longitude': '1.314',
                               'addr_street': 'Fakestreet 123',
                               'addr_zipcode': '1000',
                               'addr_location': 'Faketown',
                               'description': 'Place to be'}
        self.location_depot = Location.objects.create(**location_data_depot)

    def set_up_depots(self):
        """
        depots
        """
        depot_data = {
            'name': 'depot',
            'contact': self.member,
            'weekday': 1,
            'location': self.location_depot}
        self.depot = Depot.objects.create(**depot_data)
        depot_data = {
            'name': 'depot2',
            'contact': self.member,
            'weekday': 1,
            'location': self.location_depot}
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
                    'activation_date': timezone.now().date(),
                    'deactivation_date': None,
                    'creation_date': '2017-03-27',
                    'start_date': '2018-01-01',
                    }
        self.sub = Subscription.objects.create(**sub_data)
        self.member.join_subscription(self.sub)
        self.sub.primary_member = self.member
        self.sub.save()
        SubscriptionPart.objects.create(subscription=self.sub, type=self.sub_type)

    def set_up_area(self):
        """
        area
        """
        area_data = {'name': 'name',
                     'coordinator': self.member,
                     'auto_add_new_members': True}
        area_data2 = {'name': 'name2',
                      'coordinator': self.member,
                      'hidden': True}
        self.area = ActivityArea.objects.create(**area_data)
        self.area2 = ActivityArea.objects.create(**area_data2)
        self.member.areas.add(self.area)
        self.member.save()

    def set_up_job(self):
        """
        job_type
        """
        job_type_data = {'name': 'nameot',
                         'activityarea': self.area,
                         'default_duration': 2,
                         'location': self.location_depot}
        self.job_type = JobType.objects.create(**job_type_data)
        job_type_data2 = {'name': 'nameot2',
                          'activityarea': self.area2,
                          'default_duration': 4,
                          'location': self.location_depot}
        self.job_type2 = JobType.objects.create(**job_type_data2)
        """
        jobs
        """
        time = timezone.now() + timezone.timedelta(hours=2)
        job_data = {'slots': 1,
                    'time': time,
                    'type': self.job_type}
        job_data2 = {'slots': 6,
                     'time': time,
                     'type': self.job_type}
        self.job1 = RecuringJob.objects.create(**job_data)
        self.job2 = RecuringJob.objects.create(**job_data)
        self.job3 = RecuringJob.objects.create(**job_data)
        self.job4 = RecuringJob.objects.create(**job_data2)
        self.job5 = RecuringJob.objects.create(**job_data)
        self.past_job = RecuringJob.objects.create(
            slots=1,
            time=timezone.now() - timezone.timedelta(hours=2),
            type=self.job_type
        )
        self.infinite_job = RecuringJob.objects.create(**{
            'infinite_slots': True,
            'time': time,
            'type': self.job_type
        })
        """
        one time jobs
        """
        time = timezone.now() + timezone.timedelta(hours=2)
        one_time_job_data = {'name': 'name',
                             'activityarea': self.area,
                             'default_duration': 2,
                             'slots': 1,
                             'time': time,
                             'location': self.location_depot}
        self.one_time_job1 = OneTimeJob.objects.create(**one_time_job_data)
        one_time_job_data.update(name='name2', time=timezone.now() - timezone.timedelta(hours=2))
        self.past_one_time_job = OneTimeJob.objects.create(**one_time_job_data)
        """
        assignment
        """
        assignment_data = {'job': self.job2,
                           'member': self.member,
                           'amount': 1}
        self.assignment = Assignment.objects.create(**assignment_data)

    def assertGet(self, url, code=200, member=None):
        login_member = member or self.member
        self.client.force_login(login_member.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, code)
        return response

    def assertPost(self, url, data=None, code=200, member=None):
        login_member = member or self.member
        self.client.force_login(login_member.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, code)
        return response
