# Generated by Django 4.0.4 on 2022-05-06 10:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tecblicapp', '0030_alter_invoice_payment_status_delete_payment'),
    ]

    operations = [
        migrations.DeleteModel(
            name='gst_details',
        ),
    ]
