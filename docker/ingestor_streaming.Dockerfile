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

FROM python:3.12-slim

RUN apt-get update && apt-get install -y postgresql postgresql-contrib postgresql-client-common gdal-bin libpq-dev libgdal-dev libproj-dev \
    wget \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*7 \
    && ln /usr/bin/python3 /usr/bin/python \
    && mkdir -p /lautrer_wissen_data_integration

COPY ../requirements.txt /lautrer_wissen_data_integration/requirements.txt

ENV GDAL_CONFIG=/usr/bin/gdal-config
ENV PYTHONUNBUFFERED=1

WORKDIR "/lautrer_wissen_data_integration"

ENV PYTHONPATH=/lautrer_wissen_data_integration

RUN if [ -e requirements.txt ]; then \
        echo "Installing python packages in requirements.txt..."; \
        pip install --no-cache-dir -r requirements.txt; \
        pip install psycopg2-binary; \
    else \
        echo "requirements.txt not found!"; \
    fi

COPY ../ingestor /lautrer_wissen_data_integration/ingestor

ENTRYPOINT ["python", "-u"]
CMD ["ingestor/run_streaming_sensors.py"  "--sensor", "sensors"]  # Default script
