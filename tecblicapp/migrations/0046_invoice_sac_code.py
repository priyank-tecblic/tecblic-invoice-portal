# Generated by Django 4.0.4 on 2022-05-25 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tecblicapp', '0045_gstvalue_alter_invoice_cgst_alter_invoice_igst_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='sac_code',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
