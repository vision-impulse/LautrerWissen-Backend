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

from django import forms
from django.contrib.gis.geos import Point

class GeoForm(forms.ModelForm):
    latitude = forms.FloatField(
        required=False,
        label="Latitude (EPSG:4326)",
        help_text="Enter latitude in decimal degrees",
    )
    longitude = forms.FloatField(
        required=False,
        label="Longitude (EPSG:4326)",
        help_text="Enter longitude in decimal degrees",
    )

    class Meta:
        model = None  # set dynamically in admin
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        geom = getattr(self.instance, "geometry", None)
        if geom and geom.geom_type == "Point":
            # Always ensure geometry is in WGS84 (EPSG:4326)
            if geom.srid != 4326:
                geom.transform(4326)

            if not self.is_bound:
                self.initial["latitude"] = geom.y
                self.initial["longitude"] = geom.x


    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get("latitude")
        lon = cleaned.get("longitude")

        # Only create a geometry if both lat/lon are provided
        if lat is not None and lon is not None:
            cleaned["geometry"] = Point(lon, lat, srid=4326)
        return cleaned
