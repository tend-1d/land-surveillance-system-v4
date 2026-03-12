from .models import SiteConfiguration


def site_configuration(request):
    config = SiteConfiguration.objects.order_by('id').first()
    return {'site_config': config}
