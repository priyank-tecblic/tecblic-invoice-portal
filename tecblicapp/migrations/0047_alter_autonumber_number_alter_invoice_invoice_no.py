# Generated by Django 4.0.4 on 2022-05-25 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tecblicapp', '0046_invoice_sac_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='autonumber',
            name='number',
            field=models.IntegerField(default=5001, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='invoice_no',
            field=models.IntegerField(blank=True, default=222300001, primary_key=True, serialize=False),
        ),
    ]
