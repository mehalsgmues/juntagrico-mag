
import json

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
        # Canceled map job for filtering tests
        cls.map_job_canceled = MapJob.objects.create(
            type=cls.map_job_type,
            slots=1,
            time=timezone.now() - timezone.timedelta(hours=1),
            canceled=True,
            geo_area={
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[9.5600000, 45.420000], [9.5610000, 45.420000], [9.5610000, 45.421000], [9.5600000, 45.421000]]]
                },
                "properties": {
                    "name": "Canceled Area", "description": None
                }
            },
        )

    def test_admin_views(self):
        self.assertGet(reverse('mapjob:map'), member=self.admin)
        self.assertGet(reverse('mapjob:map_by_type', args=[self.map_job_type.id]), member=self.admin)
        self.assertGet(reverse('mapjob:list'), member=self.admin)
        self.assertGet(reverse('mapjob:edit_map_by_type', args=[self.map_job_type.id]), member=self.admin)

    def test_canceled_jobs_filtered_from_admin_views(self):
        """Canceled MapJobs should not appear in admin map views."""
        self.client.force_login(self.admin.user)
        # job_map view
        response = self.client.get(reverse('mapjob:map'))
        self.assertEqual(response.status_code, 200)
        jobs = response.context['jobs']
        self.assertNotIn(self.map_job_canceled, jobs)
        self.assertIn(self.map_job1, jobs)
        # job_map_by_type view
        response = self.client.get(reverse('mapjob:map_by_type', args=[self.map_job_type.id]))
        self.assertEqual(response.status_code, 200)
        jobs = response.context['jobs']
        self.assertNotIn(self.map_job_canceled, jobs)
        # edit_map_by_type view
        response = self.client.get(reverse('mapjob:edit_map_by_type', args=[self.map_job_type.id]))
        self.assertEqual(response.status_code, 200)
        job_ids = [area['properties']['id'] for area in response.context['map_job_data']['data']]
        self.assertNotIn(self.map_job_canceled.id, job_ids)
        self.assertIn(self.map_job1.id, job_ids)

    def test_queryset_not_canceled(self):
        """The not_canceled queryset method should exclude canceled jobs."""
        all_count = MapJob.objects.count()
        not_canceled_count = MapJob.objects.not_canceled().count()
        self.assertEqual(all_count, not_canceled_count + 1)  # 1 canceled job
        self.assertNotIn(self.map_job_canceled, MapJob.objects.not_canceled())

    def test_queryset_active_excludes_canceled(self):
        """The active queryset method should exclude both completed and canceled jobs."""
        active = MapJob.objects.active()
        self.assertNotIn(self.map_job_canceled, active)

    def test_edit_api(self):
        # Test save geo area
        new_geo_area = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[9.5479748, 45.419413], [9.5488224, 45.41905], [9.5503352, 45.4192242], [9.5479748, 45.419413]]]
            },
            "properties": {"name": "Updated Area"}
        }
        self.client.force_login(self.admin.user)
        response = self.client.post(
            reverse('mapjob:save_geo_area', args=[self.map_job1.id]),
            data=json.dumps({'geo_area': new_geo_area, 'name': 'Updated Area'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.map_job1.refresh_from_db()
        self.assertEqual(self.map_job1.geo_area['properties']['name'], 'Updated Area')

    def test_save_geo_area_invalid_json(self):
        """save_geo_area should return 400 for invalid JSON."""
        self.client.force_login(self.admin.user)
        response = self.client.post(
            reverse('mapjob:save_geo_area', args=[self.map_job1.id]),
            data='not json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_save_geo_area_missing_geo_area(self):
        """save_geo_area should return 400 when geo_area is missing."""
        self.client.force_login(self.admin.user)
        response = self.client.post(
            reverse('mapjob:save_geo_area', args=[self.map_job1.id]),
            data=json.dumps({'name': 'No geo'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_create_map_job_api(self):
        new_geo_area = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[9.5479748, 45.419413], [9.5488224, 45.41905], [9.5503352, 45.4192242], [9.5479748, 45.419413]]]
            },
            "properties": {"name": "New Area"}
        }
        count_before = MapJob.objects.count()
        self.client.force_login(self.admin.user)
        response = self.client.post(
            reverse('mapjob:create_map_job'),
            data=json.dumps({'geo_area': new_geo_area, 'type_id': self.map_job_type.id, 'name': 'New Area'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(MapJob.objects.count(), count_before + 1)
        new_job = MapJob.objects.get(id=data['job_id'])
        self.assertEqual(new_job.geo_area['properties']['name'], 'New Area')

    def test_create_map_job_missing_fields(self):
        """create_map_job should return 400 when required fields are missing."""
        self.client.force_login(self.admin.user)
        response = self.client.post(
            reverse('mapjob:create_map_job'),
            data=json.dumps({'geo_area': None, 'type_id': None}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_get_map_job_info_api(self):
        """get_map_job_info should return assignment data."""
        self.client.force_login(self.admin.user)
        response = self.client.get(reverse('mapjob:get_map_job_info', args=[self.map_job1.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['id'], self.map_job1.id)
        self.assertEqual(data['name'], 'Area')
        self.assertEqual(data['canceled'], False)
        self.assertEqual(data['assignment_count'], 0)
        self.assertEqual(data['member_names'], [])

    def test_get_map_job_info_with_assignments(self):
        """get_map_job_info should include member names when assignments exist."""
        self.map_job1.assign(self.member2)
        self.client.force_login(self.admin.user)
        response = self.client.get(reverse('mapjob:get_map_job_info', args=[self.map_job1.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['assignment_count'], 1)
        self.assertEqual(len(data['member_names']), 1)

    def test_delete_map_job_no_assignments(self):
        """delete_map_job should succeed when no assignments exist."""
        count_before = MapJob.objects.count()
        self.client.force_login(self.admin.user)
        response = self.client.post(reverse('mapjob:delete_map_job', args=[self.map_job1.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(MapJob.objects.count(), count_before - 1)

    def test_delete_map_job_with_assignments(self):
        """delete_map_job should return 409 when assignments exist."""
        self.map_job1.assign(self.member2)
        self.client.force_login(self.admin.user)
        response = self.client.post(reverse('mapjob:delete_map_job', args=[self.map_job1.id]))
        self.assertEqual(response.status_code, 409)
        data = response.json()
        self.assertFalse(data['success'])
        # Job should still exist
        self.assertTrue(MapJob.objects.filter(id=self.map_job1.id).exists())

    def test_cancel_map_job(self):
        """cancel_map_job should set the canceled flag."""
        self.assertFalse(self.map_job1.canceled)
        self.client.force_login(self.admin.user)
        response = self.client.post(reverse('mapjob:cancel_map_job', args=[self.map_job1.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.map_job1.refresh_from_db()
        self.assertTrue(self.map_job1.canceled)

    def test_cancel_map_job_removes_from_views(self):
        """A canceled MapJob should no longer appear in admin map views."""
        self.client.force_login(self.admin.user)
        # Cancel the job
        self.client.post(reverse('mapjob:cancel_map_job', args=[self.map_job1.id]))
        self.map_job1.refresh_from_db()
        self.assertTrue(self.map_job1.canceled)
        # Check it's filtered out
        response = self.client.get(reverse('mapjob:edit_map_by_type', args=[self.map_job_type.id]))
        self.assertEqual(response.status_code, 200)
        job_ids = [area['properties']['id'] for area in response.context['map_job_data']['data']]
        self.assertNotIn(self.map_job1.id, job_ids)

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
