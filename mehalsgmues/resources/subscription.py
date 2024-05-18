import datetime

from django.db.models import Count, Q
from import_export.fields import Field
from import_export.widgets import DecimalWidget
from juntagrico.config import Config
from juntagrico.dao.subscriptiontypedao import SubscriptionTypeDao

from juntagrico.entity.subs import Subscription
from juntagrico.resources import ModQuerysetModelResource
from juntagrico.util.models import q_isactive


class SubscriptionByTypeResource(ModQuerysetModelResource):
    members = Field('recipients_names')
    email = Field('primary_member__email')
    total = Field('price', widget=DecimalWidget())

    def get_fields(self):
        # create a field for each type dynamically
        self.fields.update({
            'EAT ' + str(subs_type.id): Field(f'type{subs_type.id}_count', 'EAT ' + str(subs_type.price))
            for subs_type in SubscriptionTypeDao.get_all()
        })
        return super().get_fields()

    def update_queryset(self, queryset):
        today = datetime.date.today()
        for subs_type in SubscriptionTypeDao.get_all():
            queryset = queryset.annotate(**{
                f'type{subs_type.id}_count':
                    Count('parts', filter=Q(parts__type__id=subs_type.id) & Q(parts__activation_date__lte=today) & ~Q(
                        parts__deactivation_date__lte=today))
            })
        return queryset.filter(q_isactive())

    class Meta:
        model = Subscription
        fields = ('members', 'email', 'total')
        export_order = fields
        name = Config.vocabulary('subscription_pl') + ' nach Typ'
