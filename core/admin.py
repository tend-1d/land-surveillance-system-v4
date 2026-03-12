from django.contrib import admin
from .models import AOI, Alert, AnalysisJob, AuditLog, NotificationContact, SiteConfiguration, VerificationReport


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Branding', {'fields': ('site_title', 'tagline', 'hero_title', 'hero_text')}),
        ('Images', {'fields': ('hero_image_url', 'dashboard_image_url', 'field_image_url')}),
        ('Operations', {'fields': ('operations_email', 'operations_phone', 'footer_text')}),
    )


@admin.register(AOI)
class AOIAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'monitoring_type', 'alert_threshold', 'is_active', 'created_at')
    list_filter = ('monitoring_type', 'region', 'is_active')
    list_editable = ('is_active', 'alert_threshold')
    search_fields = ('name', 'region', 'notes')


@admin.register(NotificationContact)
class NotificationContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'region', 'phone_number', 'email', 'active', 'notify_sms', 'notify_email')
    list_filter = ('organization', 'region', 'active', 'notify_sms', 'notify_email')
    list_editable = ('active', 'notify_sms', 'notify_email')
    search_fields = ('name', 'phone_number', 'email', 'organization', 'region')


@admin.register(AnalysisJob)
class AnalysisJobAdmin(admin.ModelAdmin):
    list_display = ('aoi', 'start_date', 'end_date', 'status', 'detections_count', 'engine_name', 'created_at')
    list_filter = ('status', 'engine_name', 'aoi__monitoring_type')
    search_fields = ('aoi__name', 'summary')
    readonly_fields = ('created_at', 'completed_at')


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'aoi', 'alert_type', 'status', 'confidence_score', 'area_hectares', 'detection_date')
    list_filter = ('status', 'alert_type', 'aoi__monitoring_type', 'aoi__region')
    list_editable = ('status',)
    search_fields = ('title', 'aoi__name', 'notes', 'detection_source')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(VerificationReport)
class VerificationReportAdmin(admin.ModelAdmin):
    list_display = ('alert', 'decision', 'verified_by', 'created_at')
    list_filter = ('decision',)
    search_fields = ('alert__title', 'verified_by__username', 'notes')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'alert', 'created_at')
    search_fields = ('action', 'details')
    readonly_fields = ('created_at',)
