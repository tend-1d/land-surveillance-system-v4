# AI Powered Land Surveillance System — Professional Edition

This package is a more polished Django build with:
- professional Bootstrap user interface
- admin backend for updating portal content, AOIs, alerts, jobs, contacts, and verification data
- live map with street and satellite basemaps
- alert exports to CSV and GeoJSON
- email notifications and SMS-ready logging
- optional hooks for Africa's Talking SMS and Google Earth Engine
- editable site branding and operations contact details in the admin backend

## Quick start
```bash
python -m venv venv
# Windows
venv\Scriptsctivate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata core/fixtures/sample_data.json
python manage.py runserver
```

Open:
- Home: http://127.0.0.1:8000/
- Login: http://127.0.0.1:8000/login/
- Admin: http://127.0.0.1:8000/admin/
- Live map: http://127.0.0.1:8000/live-map/

## Admin backend
Use the admin backend to update:
- Site configuration and homepage content
- Areas of interest
- Notification contacts
- Alerts and alert status
- Analysis jobs
- Verification reports

## Email and SMS
By default:
- email prints to the console backend
- SMS logs to `sms_outbox.log`

To enable real services:
- set `EMAIL_*` environment variables for SMTP
- set `SMS_BACKEND=africastalking` and provide Africa's Talking credentials

## Real imagery integration
The app includes an optional Earth Engine hook. To activate it, install the extra packages and configure:
- `DETECTION_BACKEND=earthengine`
- `GEE_SERVICE_ACCOUNT`
- `GEE_PRIVATE_KEY_FILE`

Without those credentials, the project uses the built-in prototype detector so the workflow still runs end to end.

## Notes on images
The professional photo sections use remote forest photography URLs. Replace them in **Site configuration** if you want your own hosted images or fully offline assets.
