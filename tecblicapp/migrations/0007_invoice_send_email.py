# Generated by Django 4.0.4 on 2022-05-02 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tecblicapp', '0006_clientdetail_clientemail'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='send_email',
            field=models.BooleanField(default=False),
        ),
    ]
