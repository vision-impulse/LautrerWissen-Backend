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
 
from rest_framework import serializers
from .models import MapLayerGroup, MapLayer


class MapLayerSerializer(serializers.ModelSerializer):
    sublayers = serializers.SerializerMethodField()
    legendurl = serializers.SerializerMethodField()
    attribution = serializers.SerializerMethodField()

    class Meta:
        model = MapLayer
        fields = ['name', 'visible', 'color', 'url', 'sublayers', 'legendurl', 'attribution']

    def get_sublayers(self, obj):
        sublayers = obj.sublayers.all()
        if sublayers.exists():
            return MapLayerSerializer(sublayers, many=True).data
        return []

    def get_legendurl(self, obj):
        return obj.legend_url
    
    def get_attribution(self, obj):
        return {"source": obj.attribution_source, 
                "license": obj.attribution_license,
                "url": obj.attribution_url}

class MapLayerGroupSerializer(serializers.ModelSerializer):
    layers = serializers.SerializerMethodField()

    class Meta:
        model = MapLayerGroup
        fields = ('title', 'color', 'layers',)


    def get_layers(self, obj):
        # Only top-level layers (exclude sublayers)
        top_layers = obj.layers.filter(parent__isnull=True)
        return MapLayerSerializer(top_layers, many=True).data
