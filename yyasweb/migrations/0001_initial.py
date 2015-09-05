# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Auction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('minPrice', models.DecimalField(max_digits=10, decimal_places=2)),
                ('maxPrice', models.DecimalField(max_digits=10, decimal_places=2)),
                ('maxBid', models.DateTimeField()),
                ('description', models.TextField()),
                ('startDate', models.DateTimeField(verbose_name=datetime.datetime(2015, 9, 5, 9, 45, 7, 648341, tzinfo=utc))),
                ('endDate', models.DateTimeField()),
                ('status', models.CharField(max_length=50)),
                ('seller', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(verbose_name=datetime.datetime(2015, 9, 5, 9, 45, 7, 649247, tzinfo=utc))),
                ('price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('auction', models.ForeignKey(to='yyasweb.Auction')),
                ('bidder', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
