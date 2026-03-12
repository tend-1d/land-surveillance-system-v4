import csv
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import AOIForm, AnalysisRunForm, NotificationContactForm, VerificationReportForm
from .models import AOI, Alert, AnalysisJob, AuditLog, NotificationContact, SiteConfiguration
from .services.detection import generate_detections
from .services.notifications import notify_alert


def _status_badge(value):
    return {
        'new': 'danger',
        'under_verification': 'warning',
        'confirmed': 'success',
        'false_positive': 'secondary',
        'closed': 'dark',
    }.get(value, 'primary')


def home(request):
    config = SiteConfiguration.objects.order_by('id').first()
    context = {
        'config': config,
        'aoi_count': AOI.objects.count(),
        'alert_count': Alert.objects.count(),
        'confirmed_count': Alert.objects.filter(status='confirmed').count(),
        'latest_alerts': Alert.objects.select_related('aoi')[:3],
        'recent_aois': AOI.objects.filter(is_active=True)[:4],
    }
    return render(request, 'core/home.html', context)


@login_required
def dashboard(request):
    stats = {
        'total_alerts': Alert.objects.count(),
        'active_alerts': Alert.objects.filter(status__in=['new', 'under_verification']).count(),
        'confirmed_alerts': Alert.objects.filter(status='confirmed').count(),
        'false_positives': Alert.objects.filter(status='false_positive').count(),
        'total_area': round(Alert.objects.aggregate(total=Sum('area_hectares'))['total'] or 0, 2),
        'aoi_count': AOI.objects.count(),
        'contacts_count': NotificationContact.objects.filter(active=True).count(),
    }
    charts = list(Alert.objects.values('alert_type').annotate(total=Count('id')).order_by('-total'))
    regions = list(Alert.objects.values('aoi__region').annotate(total=Count('id')).order_by('-total'))
    jobs = AnalysisJob.objects.select_related('aoi')[:5]
    recent_alerts = Alert.objects.select_related('aoi')[:6]
    return render(request, 'core/dashboard.html', {
        'stats': stats,
        'jobs': jobs,
        'recent_alerts': recent_alerts,
        'charts': json.dumps(charts),
        'regions': json.dumps(regions),
    })


@login_required
def alerts(request):
    items = Alert.objects.select_related('aoi', 'analysis_job')
    status = request.GET.get('status')
    if status:
        items = items.filter(status=status)
    for alert in items:
        alert.badge = _status_badge(alert.status)
    return render(request, 'core/alerts.html', {'alerts': items, 'selected_status': status})


@login_required
def alert_detail(request, pk):
    alert = get_object_or_404(Alert.objects.select_related('aoi', 'analysis_job'), pk=pk)
    if request.method == 'POST':
        form = VerificationReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.alert = alert
            report.verified_by = request.user
            report.save()
            if report.decision == 'confirmed':
                alert.status = 'confirmed'
            elif report.decision == 'false_positive':
                alert.status = 'false_positive'
            else:
                alert.status = 'under_verification'
            alert.save(update_fields=['status', 'updated_at'])
            AuditLog.objects.create(action='Verification submitted', user=request.user, alert=alert, details=report.decision)
            messages.success(request, 'Verification saved successfully.')
            return redirect('alert_detail', pk=alert.pk)
    else:
        form = VerificationReportForm()
    badge = _status_badge(alert.status)
    return render(request, 'core/alert_detail.html', {'alert': alert, 'form': form, 'badge': badge})


@login_required
def aois(request):
    if request.method == 'POST':
        form = AOIForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'AOI saved.')
            return redirect('aois')
    else:
        form = AOIForm()
    return render(request, 'core/aois.html', {'aois': AOI.objects.all(), 'form': form})


@login_required
def contacts(request):
    if request.method == 'POST':
        form = NotificationContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification contact saved.')
            return redirect('contacts')
    else:
        form = NotificationContactForm()
    return render(request, 'core/contacts.html', {'contacts': NotificationContact.objects.all(), 'form': form})


@login_required
def analysis_jobs(request):
    return render(request, 'core/analysis_jobs.html', {'jobs': AnalysisJob.objects.select_related('aoi', 'requested_by')})


@login_required
def run_analysis(request):
    if request.method == 'POST':
        form = AnalysisRunForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.requested_by = request.user
            job.status = 'running'
            job.save()
            detections, engine_name = generate_detections(job.aoi, job.start_date, job.end_date)
            job.engine_name = engine_name
            created = []
            for detection in detections:
                alert = Alert.objects.create(aoi=job.aoi, analysis_job=job, **detection)
                created.append(alert)
                notify_alert(alert, actor=request.user)
            job.status = 'success'
            job.completed_at = timezone.now()
            job.detections_count = len(created)
            job.summary = f'Analysis completed with {len(created)} affected area(s) identified.'
            job.save(update_fields=['status', 'completed_at', 'detections_count', 'summary', 'engine_name'])
            messages.success(request, f'Analysis completed. {len(created)} alert(s) generated.')
            return redirect('analysis_jobs')
    else:
        form = AnalysisRunForm()
    return render(request, 'core/run_analysis.html', {'form': form})


@login_required
def live_map(request):
    recent_alerts = Alert.objects.select_related('aoi')[:10]
    return render(request, 'core/live_map.html', {'aois': AOI.objects.filter(is_active=True), 'alerts': recent_alerts})


@login_required
def reports(request):
    by_status = list(Alert.objects.values('status').annotate(total=Count('id')).order_by('-total'))
    by_region = list(Alert.objects.values('aoi__region').annotate(total=Count('id')).order_by('-total'))
    summary = {
        'alerts': Alert.objects.count(),
        'verified': Alert.objects.filter(status='confirmed').count(),
        'false_positive': Alert.objects.filter(status='false_positive').count(),
        'jobs': AnalysisJob.objects.count(),
    }
    return render(request, 'core/reports.html', {
        'summary': summary,
        'by_status': json.dumps(by_status),
        'by_region': json.dumps(by_region),
    })


@login_required
def map_data(request):
    features = []
    for aoi in AOI.objects.filter(is_active=True):
        if aoi.polygon_json:
            geometry = json.loads(aoi.polygon_json)
            if geometry.get('type') == 'Feature':
                geometry = geometry['geometry']
        else:
            geometry = {'type': 'Polygon', 'coordinates': [[
                [aoi.center_lon - 0.03, aoi.center_lat - 0.03],
                [aoi.center_lon + 0.03, aoi.center_lat - 0.03],
                [aoi.center_lon + 0.03, aoi.center_lat + 0.03],
                [aoi.center_lon - 0.03, aoi.center_lat + 0.03],
                [aoi.center_lon - 0.03, aoi.center_lat - 0.03],
            ]]}
        features.append({'type': 'Feature', 'geometry': geometry, 'properties': {'name': aoi.name, 'layer': 'aoi', 'region': aoi.region}})
    for alert in Alert.objects.select_related('aoi'):
        features.append({'type': 'Feature', 'geometry': json.loads(alert.affected_polygon_json), 'properties': {'name': alert.title, 'layer': 'alert', 'status': alert.status, 'url': alert.get_absolute_url(), 'confidence': alert.confidence_score, 'region': alert.aoi.region}})
    return JsonResponse({'type': 'FeatureCollection', 'features': features})


@login_required
def export_alerts_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="alerts.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'AOI', 'Region', 'Type', 'Latitude', 'Longitude', 'Area (ha)', 'Confidence', 'Status', 'Detection Date'])
    for a in Alert.objects.select_related('aoi'):
        writer.writerow([a.id, a.aoi.name, a.aoi.region, a.alert_type, a.latitude, a.longitude, a.area_hectares, a.confidence_score, a.status, a.detection_date])
    return response


@login_required
def export_alerts_geojson(request):
    data = {'type': 'FeatureCollection', 'features': []}
    for a in Alert.objects.select_related('aoi'):
        data['features'].append({
            'type': 'Feature',
            'geometry': json.loads(a.affected_polygon_json),
            'properties': {
                'id': a.id,
                'aoi': a.aoi.name,
                'region': a.aoi.region,
                'type': a.alert_type,
                'confidence': a.confidence_score,
                'status': a.status,
                'url': a.get_absolute_url(),
            }
        })
    return JsonResponse(data)
