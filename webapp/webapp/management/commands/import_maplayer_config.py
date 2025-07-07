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
 
import json
from django.core.management.base import BaseCommand
from frontend_config.models import MapLayerGroup, MapLayer
import os 

class Command(BaseCommand):
    help = "Import a JSON layer config into the database"

    def handle(self, *args, **kwargs):
        csv_file = os.path.join(os.getenv("APP_DATA_DIR"), "initial/config/layer_groups_import.json")
        with open(csv_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        MapLayerGroup.objects.all().delete()
        MapLayer.objects.all().delete()

        for group_order, group_data in enumerate(config):
            group, _ = MapLayerGroup.objects.get_or_create(
                title=group_data['title'],
                defaults={
                    'color': group_data.get('color', '#CCCCCC'),
                    'order': group_order
                }
            )

            for layer_order, layer_info in enumerate(group_data['layers']):
                layer = MapLayer.objects.create(
                    group=group,
                    name=layer_info["title"],
                    url=layer_info['url'],
                    visible=layer_info.get('visible', False),
                    color=layer_info.get('color', '#000000'),
                    order=layer_order,
                    parent=None
                )

                sublayers = layer_info.get('subLayers', {})
                for sub_order, layersub_info in enumerate(sublayers):
                    MapLayer.objects.create(
                        group=group,
                        parent=layer,
                        name=layersub_info['title'],
                        url=layersub_info['url'],
                        visible=layersub_info.get('visible', False),
                        color=layersub_info.get('color', '#000000'),
                        order=sub_order
                    )

        self.stdout.write(self.style.SUCCESS(" Layer configuration imported successfully."))
