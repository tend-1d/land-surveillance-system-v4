from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('alerts/', views.alerts, name='alerts'),
    path('alerts/<int:pk>/', views.alert_detail, name='alert_detail'),
    path('aois/', views.aois, name='aois'),
    path('contacts/', views.contacts, name='contacts'),
    path('analysis-jobs/', views.analysis_jobs, name='analysis_jobs'),
    path('analysis-jobs/run/', views.run_analysis, name='run_analysis'),
    path('live-map/', views.live_map, name='live_map'),
    path('reports/', views.reports, name='reports'),
    path('api/map-data/', views.map_data, name='map_data'),
    path('exports/alerts.csv', views.export_alerts_csv, name='export_alerts_csv'),
    path('exports/alerts.geojson', views.export_alerts_geojson, name='export_alerts_geojson'),
]
