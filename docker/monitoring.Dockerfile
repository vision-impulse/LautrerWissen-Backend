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

RUN apt-get update && apt-get install -y goaccess && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ../. /app

RUN mkdir -p /logs/nginx /logs/analysis /config

ENV PYTHONPATH=/app

CMD ["python", "-u", "monitoring/main.py"]