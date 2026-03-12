import hashlib
import json
import math
import random
from datetime import datetime, timedelta, timezone
from django.conf import settings

try:
    import ee
except Exception:  # pragma: no cover
    ee = None


def _seed(*parts):
    value = '|'.join(str(p) for p in parts)
    return int(hashlib.sha256(value.encode()).hexdigest()[:16], 16)


def polygon_square(lat, lon, radius_km):
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / max(1.0, 111.0 * math.cos(math.radians(lat)))
    return [[
        [lon - lon_delta, lat - lat_delta],
        [lon + lon_delta, lat - lat_delta],
        [lon + lon_delta, lat + lat_delta],
        [lon - lon_delta, lat + lat_delta],
        [lon - lon_delta, lat - lat_delta],
    ]]


def _prototype_detections(aoi, start_date, end_date):
    rng = random.Random(_seed(aoi.id, start_date, end_date, aoi.monitoring_type, aoi.alert_threshold))
    count = rng.randint(1, 3)
    detections = []
    base_area = {'forest': 3.8, 'water': 2.1, 'agri': 4.5}[aoi.monitoring_type]
    alert_type = {
        'forest': 'Forest Disturbance',
        'water': 'Water Stress',
        'agri': 'Crop Stress',
    }[aoi.monitoring_type]

    for idx in range(count):
        lat = aoi.center_lat + rng.uniform(-0.015, 0.015)
        lon = aoi.center_lon + rng.uniform(-0.015, 0.015)
        area = round(base_area + rng.uniform(0.4, 4.8), 2)
        confidence = round(min(0.98, max(0.55, aoi.alert_threshold + rng.uniform(0.35, 0.6))), 2)
        polygon = polygon_square(lat, lon, max(0.12, math.sqrt(area) * 0.18))
        detections.append({
            'title': f'{alert_type} #{idx + 1} - {aoi.name}',
            'alert_type': alert_type,
            'latitude': round(lat, 6),
            'longitude': round(lon, 6),
            'affected_polygon_json': json.dumps({'type': 'Polygon', 'coordinates': polygon}),
            'area_hectares': area,
            'confidence_score': confidence,
            'detection_date': datetime.now(timezone.utc),
            'notes': 'Automated detection from the built-in prototype engine. Switch DETECTION_BACKEND=earthengine and configure credentials for live imagery.',
            'before_reference': f'Baseline window: {start_date}',
            'after_reference': f'Observation window: {end_date}',
            'detection_source': 'Prototype detector',
        })
    return detections, 'Prototype detector'


def _init_gee():
    if not ee:
        raise RuntimeError('earthengine-api is not installed.')
    credentials = ee.ServiceAccountCredentials(settings.GEE_SERVICE_ACCOUNT, settings.GEE_PRIVATE_KEY_FILE)
    ee.Initialize(credentials)


def _earthengine_detections(aoi, start_date, end_date):
    _init_gee()
    if aoi.polygon_json:
        region = ee.Geometry(json.loads(aoi.polygon_json))
    else:
        region = ee.Geometry.Point([aoi.center_lon, aoi.center_lat]).buffer(aoi.radius_km * 1000).bounds()

    def mask_clouds(img):
        qa = img.select('QA60')
        cloud = 1 << 10
        cirrus = 1 << 11
        mask = qa.bitwiseAnd(cloud).eq(0).And(qa.bitwiseAnd(cirrus).eq(0))
        return img.updateMask(mask).divide(10000)

    def add_ndvi(img):
        ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI')
        return img.addBands(ndvi)

    start = datetime.fromisoformat(str(start_date))
    end = datetime.fromisoformat(str(end_date))
    delta = max(14, (end - start).days)
    prev_start = (start - timedelta(days=delta)).strftime('%Y-%m-%d')
    prev_end = start.strftime('%Y-%m-%d')

    current = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(region).filterDate(str(start_date), str(end_date)).map(mask_clouds).map(add_ndvi).median()
    baseline = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(region).filterDate(prev_start, prev_end).map(mask_clouds).map(add_ndvi).median()
    ndvi_change = current.select('NDVI').subtract(baseline.select('NDVI')).rename('NDVI_CHANGE')
    disturbed = ndvi_change.lt(-float(aoi.alert_threshold)).selfMask()
    vectors = disturbed.reduceToVectors(geometry=region, scale=20, geometryType='polygon', reducer=ee.Reducer.countEvery(), maxPixels=1e8)
    fc = vectors.getInfo()

    detections = []
    for idx, feat in enumerate(fc.get('features', [])[:10], start=1):
        geom = feat['geometry']
        ring = geom['coordinates'][0]
        lons = [p[0] for p in ring]
        lats = [p[1] for p in ring]
        lon = sum(lons) / len(lons)
        lat = sum(lats) / len(lats)
        area_m2 = ee.Geometry(geom).area().getInfo()
        area_ha = round(area_m2 / 10000, 2)
        confidence = round(min(0.99, 0.6 + area_ha / 20), 2)
        detections.append({
            'title': f'Forest Disturbance #{idx} - {aoi.name}',
            'alert_type': 'Forest Disturbance',
            'latitude': round(lat, 6),
            'longitude': round(lon, 6),
            'affected_polygon_json': json.dumps(geom),
            'area_hectares': area_ha,
            'confidence_score': confidence,
            'detection_date': datetime.now(timezone.utc),
            'notes': 'Automated detection from Google Earth Engine Sentinel-2 NDVI change analysis.',
            'before_reference': f'Baseline window: {prev_start} to {prev_end}',
            'after_reference': f'Observation window: {start_date} to {end_date}',
            'detection_source': 'Google Earth Engine',
        })
    return detections, 'Google Earth Engine Sentinel-2 NDVI'


def generate_detections(aoi, start_date, end_date):
    backend = getattr(settings, 'DETECTION_BACKEND', 'prototype')
    if backend == 'earthengine' and settings.GEE_SERVICE_ACCOUNT and settings.GEE_PRIVATE_KEY_FILE:
        try:
            return _earthengine_detections(aoi, start_date, end_date)
        except Exception:
            return _prototype_detections(aoi, start_date, end_date)
    return _prototype_detections(aoi, start_date, end_date)
