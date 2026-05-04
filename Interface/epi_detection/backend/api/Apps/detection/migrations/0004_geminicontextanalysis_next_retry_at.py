from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('detection', '0003_noncompliancestate_person_key_and_bbox'),
    ]

    operations = [
        migrations.AddField(
            model_name='geminicontextanalysis',
            name='next_retry_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]