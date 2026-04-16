from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guests', '0008_guest_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='guest',
            name='checked_in',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='guest',
            name='checked_in_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]