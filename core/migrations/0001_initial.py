from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AOI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('region', models.CharField(blank=True, max_length=120)),
                ('monitoring_type', models.CharField(choices=[('forest', 'Forest Guard'), ('water', 'Water Guard'), ('agri', 'Agri Guard')], default='forest', max_length=20)),
                ('center_lat', models.FloatField()),
                ('center_lon', models.FloatField()),
                ('radius_km', models.FloatField(default=3.0)),
                ('polygon_json', models.TextField(blank=True, help_text='Optional GeoJSON polygon coordinates.')),
                ('alert_threshold', models.FloatField(default=0.3)),
                ('is_active', models.BooleanField(default=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='NotificationContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('organization', models.CharField(default='KWS', max_length=120)),
                ('region', models.CharField(blank=True, max_length=120)),
                ('phone_number', models.CharField(blank=True, max_length=30)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('active', models.BooleanField(default=True)),
                ('notify_sms', models.BooleanField(default=True)),
                ('notify_email', models.BooleanField(default=True)),
                ('receive_all_regions', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='SiteConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_title', models.CharField(default='AI Powered Land Surveillance System', max_length=160)),
                ('tagline', models.CharField(default='Near-real-time environmental monitoring, alerting, and officer verification.', max_length=255)),
                ('hero_title', models.CharField(default='Protect forests with faster digital intelligence', max_length=255)),
                ('hero_text', models.TextField(default='Monitor protected areas, run automated scans, review georeferenced alerts, and notify field teams through one operations portal.')),
                ('hero_image_url', models.URLField(blank=True, default='https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1600&q=80')),
                ('dashboard_image_url', models.URLField(blank=True, default='https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80')),
                ('field_image_url', models.URLField(blank=True, default='https://images.unsplash.com/photo-1473773508845-188df298d2d1?auto=format&fit=crop&w=1200&q=80')),
                ('operations_email', models.EmailField(blank=True, default='ops@example.com', max_length=254)),
                ('operations_phone', models.CharField(blank=True, default='+254700000000', max_length=40)),
                ('footer_text', models.CharField(default='AI Powered Land Surveillance System', max_length=255)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'Site configuration', 'verbose_name_plural': 'Site configuration'},
        ),
        migrations.CreateModel(
            name='AnalysisJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('success', 'Success'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('summary', models.TextField(blank=True)),
                ('detections_count', models.PositiveIntegerField(default=0)),
                ('engine_name', models.CharField(default='Prototype detector', max_length=120)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('aoi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analysis_jobs', to='core.aoi')),
                ('requested_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=160)),
                ('alert_type', models.CharField(default='Forest Disturbance', max_length=80)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('affected_polygon_json', models.TextField(help_text='GeoJSON polygon geometry as text.')),
                ('area_hectares', models.FloatField(default=0)),
                ('confidence_score', models.FloatField(default=0)),
                ('status', models.CharField(choices=[('new', 'New'), ('under_verification', 'Under Verification'), ('confirmed', 'Confirmed'), ('false_positive', 'False Positive'), ('closed', 'Closed')], default='new', max_length=30)),
                ('detection_date', models.DateTimeField()),
                ('detection_source', models.CharField(default='Prototype detector', max_length=160)),
                ('before_reference', models.CharField(blank=True, max_length=255)),
                ('after_reference', models.CharField(blank=True, max_length=255)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('analysis_job', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alerts', to='core.analysisjob')),
                ('aoi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to='core.aoi')),
            ],
            options={'ordering': ['-detection_date']},
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=160)),
                ('details', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('alert', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.alert')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='VerificationReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('decision', models.CharField(choices=[('confirmed', 'Confirmed'), ('false_positive', 'False Positive'), ('under_investigation', 'Under Investigation')], max_length=30)),
                ('notes', models.TextField()),
                ('photo', models.ImageField(blank=True, null=True, upload_to='verification_photos/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('alert', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='verification_reports', to='core.alert')),
                ('verified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
