# Generated by Django 4.0.8 on 2022-10-27 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0028_alter_accounts_uid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accounts',
            name='uid',
            field=models.CharField(default='<function uuid4 at 0x7f6608c6e710>', max_length=200),
        ),
    ]