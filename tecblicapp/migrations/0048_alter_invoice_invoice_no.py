# Generated by Django 4.0.4 on 2022-05-25 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tecblicapp', '0047_alter_autonumber_number_alter_invoice_invoice_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='invoice_no',
            field=models.IntegerField(blank=True, primary_key=True, serialize=False),
        ),
    ]
