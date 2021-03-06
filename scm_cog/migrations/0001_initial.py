# Generated by Django 3.2.4 on 2021-07-21 08:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Pch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pch_name', models.CharField(max_length=50)),
                ('sigla', models.CharField(max_length=4)),
                ('ugs_number', models.IntegerField()),
                ('created_at', models.DateField(auto_now_add=True)),
            ],
            options={
                'db_table': 'pchs',
            },
        ),
        migrations.CreateModel(
            name='Tmpevent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ug', models.IntegerField()),
                ('data_stop', models.DateTimeField(blank=True, null=True)),
                ('data_start', models.DateTimeField(blank=True, null=True)),
                ('interruption', models.CharField(max_length=75)),
                ('description', models.CharField(max_length=75)),
                ('explain', models.CharField(max_length=150)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('pch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scm_cog.pch')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'tmp_event',
                'unique_together': {('data_stop', 'ug', 'pch')},
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_stop', models.DateTimeField(blank=True, null=True)),
                ('data_start', models.DateTimeField(blank=True, null=True)),
                ('interruption', models.CharField(max_length=75)),
                ('description', models.CharField(max_length=75)),
                ('explain', models.CharField(max_length=150)),
                ('ug', models.IntegerField()),
                ('created_at', models.DateField(auto_now_add=True)),
                ('pch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scm_cog.pch')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'events',
                'unique_together': {('data_stop', 'ug', 'pch')},
            },
        ),
    ]
