# Generated by Django 4.0.8 on 2023-01-08 19:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('juntagrico', '0037_post_1_5'),
    ]

    operations = [
        migrations.CreateModel(
            name='MapJob',
            fields=[
                ('recuringjob_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='juntagrico.recuringjob')),
                ('geo_area', models.JSONField(verbose_name='geo_area')),
            ],
            options={
                'verbose_name': 'Job mit Fläche',
                'verbose_name_plural': 'Job mit Fläche',
            },
            bases=('juntagrico.recuringjob',),
        ),
    ]
