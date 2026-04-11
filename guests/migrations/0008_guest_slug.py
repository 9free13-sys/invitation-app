from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guests', '0007_remove_guest_allowed_companions_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='guest',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]