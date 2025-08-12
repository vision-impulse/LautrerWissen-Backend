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

# Make django migrations
echo "Migrations..."
python3 manage.py makemigrations
python3 manage.py migrate

# Create superuser if not exists
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
EOF
fi

python3 manage.py import_maplayer_config
python3 manage.py import_data_pipelines
python3 manage.py import_dashboards
python3 manage.py import_demographics
python3 manage.py import_elections
python3 manage.py import_fieldtest_measurements

# Add collect static
echo "Collect static files..."
python3 manage.py collectstatic --noinput -v=2

# Startup daphne
echo "Start daphne as ASGI..."
daphne -b 0.0.0.0 -p $BACKEND_PORT webapp.asgi:application
