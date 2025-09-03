from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='jellyfin_item_id',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
    ]



