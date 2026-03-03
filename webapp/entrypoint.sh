#!/usr/bin/env bash
# Copyright (c) 2025 Vision Impulse GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Authors: Benjamin Bischke

set -euo pipefail

# This script is meant to be called from within a docker container
cd /lautrer_wissen_backend/webapp

# ----------------------------------------------------------------------------------------
# Make django migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# ----------------------------------------------------------------------------------------
# Create superuser if not exists
python manage.py shell << EOF

from django.contrib.auth import get_user_model

def load_secrets(file_path):
    secrets = {}
    if not os.path.exists(file_path):
        return secrets

    with open(file_path) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                secrets[key] = value
    return secrets

django_secrets = load_secrets("/run/secrets/django_secrets")
DJANGO_SUPERUSER_USERNAME = django_secrets.get("DJANGO_SUPERUSER_USERNAME") 
DJANGO_SUPERUSER_EMAIL = django_secrets.get("DJANGO_SUPERUSER_EMAIL") 
DJANGO_SUPERUSER_PASSWORD = django_secrets.get("DJANGO_SUPERUSER_PASSWORD") 

User = get_user_model()
if not User.objects.filter(username=DJANGO_SUPERUSER_USERNAME).exists():
    User.objects.create_superuser(DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD)
EOF

# ----------------------------------------------------------------------------------------
# Import seed data content (static, no API existing) (app: lautrer_wissen)
python3 manage.py import_dashboards
python3 manage.py import_elections
python3 manage.py import_fieldtests

# Import seed configuration for map sidebar (app: frontend_config)
python3 manage.py import_maplayer_config
python3 manage.py import_model_field_config

# Import seed configuration for data pipelines (app: pipeline_manager)
python3 manage.py import_data_pipeline_schedules
python3 manage.py import_data_pipelines

# ----------------------------------------------------------------------------------------
# Add collect static
echo "Collect static files..."
python3 manage.py collectstatic --noinput -v=2

# ----------------------------------------------------------------------------------------
# Startup daphne
echo "Start daphne as ASGI..."
daphne -b 0.0.0.0 -p $DJANGO_BACKEND_PORT webapp.asgi:application
