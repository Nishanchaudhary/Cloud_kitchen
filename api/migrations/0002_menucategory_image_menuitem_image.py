# Generated by Django 5.1.6 on 2025-02-13 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='menucategory',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='category_images/'),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='menuitem_images/'),
        ),
    ]
