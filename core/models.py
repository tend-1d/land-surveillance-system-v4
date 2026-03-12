from django.conf import settings
from django.db import models
from django.urls import reverse


class SiteConfiguration(models.Model):
    site_title = models.CharField(max_length=160, default='AI Powered Land Surveillance System')
    tagline = models.CharField(max_length=255, default='Near-real-time environmental monitoring, alerting, and officer verification.')
    hero_title = models.CharField(max_length=255, default='Protect forests with faster digital intelligence')
    hero_text = models.TextField(default='Monitor protected areas, run automated scans, review georeferenced alerts, and notify field teams through one operations portal.')
    hero_image_url = models.URLField(blank=True, default='https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1600&q=80')
    dashboard_image_url = models.URLField(blank=True, default='https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80')
    field_image_url = models.URLField(blank=True, default='https://images.unsplash.com/photo-1473773508845-188df298d2d1?auto=format&fit=crop&w=1200&q=80')
    operations_email = models.EmailField(blank=True, default='ops@example.com')
    operations_phone = models.CharField(max_length=40, blank=True, default='+254700000000')
    footer_text = models.CharField(max_length=255, default='AI Powered Land Surveillance System')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site configuration'
        verbose_name_plural = 'Site configuration'

    def __str__(self):
        return 'Site configuration'


class AOI(models.Model):
    FOREST = 'forest'
    WATER = 'water'
    AGRI = 'agri'
    MONITORING_CHOICES = [
        (FOREST, 'Forest Guard'),
        (WATER, 'Water Guard'),
        (AGRI, 'Agri Guard'),
    ]
    name = models.CharField(max_length=120)
    region = models.CharField(max_length=120, blank=True)
    monitoring_type = models.CharField(max_length=20, choices=MONITORING_CHOICES, default=FOREST)
    center_lat = models.FloatField()
    center_lon = models.FloatField()
    radius_km = models.FloatField(default=3.0)
    polygon_json = models.TextField(blank=True, help_text='Optional GeoJSON polygon coordinates.')
    alert_threshold = models.FloatField(default=0.30)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class NotificationContact(models.Model):
    name = models.CharField(max_length=120)
    organization = models.CharField(max_length=120, default='KWS')
    region = models.CharField(max_length=120, blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    active = models.BooleanField(default=True)
    notify_sms = models.BooleanField(default=True)
    notify_email = models.BooleanField(default=True)
    receive_all_regions = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.organization})'


class AnalysisJob(models.Model):
    PENDING = 'pending'
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILED = 'failed'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (RUNNING, 'Running'),
        (SUCCESS, 'Success'),
        (FAILED, 'Failed'),
    ]
    aoi = models.ForeignKey(AOI, on_delete=models.CASCADE, related_name='analysis_jobs')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    summary = models.TextField(blank=True)
    detections_count = models.PositiveIntegerField(default=0)
    engine_name = models.CharField(max_length=120, default='Prototype detector')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.aoi.name} ({self.start_date} to {self.end_date})'


class Alert(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('under_verification', 'Under Verification'),
        ('confirmed', 'Confirmed'),
        ('false_positive', 'False Positive'),
        ('closed', 'Closed'),
    ]
    aoi = models.ForeignKey(AOI, on_delete=models.CASCADE, related_name='alerts')
    analysis_job = models.ForeignKey(AnalysisJob, on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts')
    title = models.CharField(max_length=160)
    alert_type = models.CharField(max_length=80, default='Forest Disturbance')
    latitude = models.FloatField()
    longitude = models.FloatField()
    affected_polygon_json = models.TextField(help_text='GeoJSON polygon geometry as text.')
    area_hectares = models.FloatField(default=0)
    confidence_score = models.FloatField(default=0)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='new')
    detection_date = models.DateTimeField()
    detection_source = models.CharField(max_length=160, default='Prototype detector')
    before_reference = models.CharField(max_length=255, blank=True)
    after_reference = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-detection_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('alert_detail', args=[self.pk])


class VerificationReport(models.Model):
    DECISIONS = [
        ('confirmed', 'Confirmed'),
        ('false_positive', 'False Positive'),
        ('under_investigation', 'Under Investigation'),
    ]
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='verification_reports')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    decision = models.CharField(max_length=30, choices=DECISIONS)
    notes = models.TextField()
    photo = models.ImageField(upload_to='verification_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.alert.title} - {self.decision}'


class AuditLog(models.Model):
    action = models.CharField(max_length=160)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    alert = models.ForeignKey(Alert, on_delete=models.SET_NULL, null=True, blank=True)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.action
