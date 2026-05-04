from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('detection', '0002_noncompliancestate_geminicontextanalysis_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='noncompliancestate',
            name='last_known_bbox',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='noncompliancestate',
            name='person_key',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
        migrations.AddIndex(
            model_name='noncompliancestate',
            index=models.Index(fields=['camera', 'person_key', 'is_active'], name='detection_n_camera__41abca_idx'),
        ),
    ]