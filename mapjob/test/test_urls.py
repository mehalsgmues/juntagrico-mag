
from django.urls import reverse
from django.utils import timezone
from juntagrico.entity.jobs import JobType
from juntagrico.tests import JuntagricoTestCase

from mapjob.models import MapJob


class MapJobTests(JuntagricoTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.map_job_type = JobType.objects.create(
            name='mapjob campaign',
            activityarea=cls.area,
            default_duration=2,
            location=cls.create_location('mapjob location'),
        )
        cls.map_job1 = MapJob.objects.create(
            type=cls.map_job_type,
            slots=2,
            time=timezone.now() - timezone.timedelta(hours=2),
            geo_area={
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[9.5479748, 45.419413], [9.5488224, 45.41905], [9.5503352, 45.4192242]]]
                },
                "properties": {
                    "name": "Area", "description": None
                }
            },
        )

    def test_admin_views(self):
        self.assertGet(reverse('mapjob:map'), member=self.admin)
        self.assertGet(reverse('mapjob:map_by_type', args=[self.map_job_type.id]), member=self.admin)
        self.assertGet(reverse('mapjob:list'), member=self.admin)

    def test_member_views(self):
        self.assertGet(reverse('mapjob:available_areas'), member=self.member2)
        self.map_job1.assign(self.member2)
        self.assertGet(reverse('mapjob:member_dashboard'), member=self.member2)

    def test_member_actions(self):
        self.assertGet(reverse('mapjob:register', args=[self.map_job1.id]), 302, self.member2)
        self.assertIn(self.member2, self.map_job1.participants)
        self.assertGet(reverse('mapjob:set_progress', args=[self.map_job1.id, 'PU']), 302, self.member2)
        self.map_job1.refresh_from_db()
        self.assertEqual(self.map_job1.progress, 'PU')
        self.assertGet(reverse('mapjob:set_job_pickup_location', args=[self.map_job1.id]), 302, member=self.member2)
        self.assertGet(reverse('mapjob:set_all_pickup_location'), 302, self.member2)
        self.assertGet(reverse('mapjob:pickup'), 302, self.member2)
        self.assertGet(reverse('mapjob:return'), 302, self.member2)
        self.assertGet(reverse('mapjob:complete'), 302, self.member2)

    def test_import(self):
        self.assertGet(reverse('mapjob:import'), member=self.admin)
        self.assertGet(reverse('mapjob:select_entries'), code=302, member=self.admin)
