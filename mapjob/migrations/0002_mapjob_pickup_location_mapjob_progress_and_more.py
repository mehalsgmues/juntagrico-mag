# Generated by Django 4.0.10 on 2024-01-21 21:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('juntagrico', '0037_post_1_5'),
        ('mapjob', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PickupLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('available_flyers', models.IntegerField(default=0, verbose_name='Verfügbare Flyer')),
                ('location',
                 models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='juntagrico.location')),
            ],
            options={
                'verbose_name': 'Abholort',
                'verbose_name_plural': 'Abholorte',
            },
        ),
        migrations.AddField(
            model_name='mapjob',
            name='pickup_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='mapjob.pickuplocation', verbose_name='Abholort'),
        ),
        migrations.AddField(
            model_name='mapjob',
            name='progress',
            field=models.CharField(
                choices=[('OP', 'Offen'), ('NM', 'Braucht mehr Flyer'), ('PU', 'Abgeholt'), ('DL', 'Verteilt'),
                         ('CO', 'Erledigt')], default='OP', max_length=2, verbose_name='Fortschritt'),
        ),
        migrations.AddField(
            model_name='mapjob',
            name='used_flyers',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Verteilte Flyer'),
        ),
    ]
