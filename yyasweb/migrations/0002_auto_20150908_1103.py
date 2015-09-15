# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('yyasweb', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auction',
            name='maxBid',
        ),
        migrations.AddField(
            model_name='auction',
            name='maxBidId',
            field=models.CharField(default=b'', max_length=20),
        ),
        migrations.AlterField(
            model_name='auction',
            name='startDate',
            field=models.DateTimeField(verbose_name=datetime.datetime(2015, 9, 8, 11, 3, 27, 27567, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='bid',
            name='time',
            field=models.DateTimeField(verbose_name=datetime.datetime(2015, 9, 8, 11, 3, 27, 28473, tzinfo=utc)),
        ),
    ]
