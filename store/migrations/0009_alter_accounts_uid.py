# Generated by Django 4.0.8 on 2022-10-17 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_alter_accounts_uid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accounts',
            name='uid',
            field=models.CharField(default='<function uuid4 at 0x7f3ccf446710>', max_length=200),
        ),
    ]