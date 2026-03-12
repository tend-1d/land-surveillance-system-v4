from django import forms
from .models import AOI, AnalysisJob, NotificationContact, VerificationReport


class VerificationReportForm(forms.ModelForm):
    class Meta:
        model = VerificationReport
        fields = ['decision', 'notes', 'photo']
        widgets = {
            'decision': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Field findings, observations, enforcement notes...'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class AnalysisRunForm(forms.ModelForm):
    class Meta:
        model = AnalysisJob
        fields = ['aoi', 'start_date', 'end_date']
        widgets = {
            'aoi': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class AOIForm(forms.ModelForm):
    class Meta:
        model = AOI
        fields = ['name', 'region', 'monitoring_type', 'center_lat', 'center_lon', 'radius_km', 'polygon_json', 'alert_threshold', 'is_active', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'monitoring_type': forms.Select(attrs={'class': 'form-select'}),
            'center_lat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'center_lon': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'radius_km': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'polygon_json': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '{"type": "Polygon", "coordinates": [[[36.0,-0.4], ...]]}'}),
            'alert_threshold': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class NotificationContactForm(forms.ModelForm):
    class Meta:
        model = NotificationContact
        fields = ['name', 'organization', 'region', 'phone_number', 'email', 'active', 'notify_sms', 'notify_email', 'receive_all_regions']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'organization': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+2547XXXXXXXX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_sms': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'receive_all_regions': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
