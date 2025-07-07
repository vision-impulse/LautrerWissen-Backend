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

import xml.etree.ElementTree as ET
from collections import OrderedDict
from ingestor.apis import XMLDownloader
from datetime import datetime


class EventCalendarDownloader(XMLDownloader):

    def __init__(self, out_dir, resource_file, logger):
        super(EventCalendarDownloader, self).__init__(out_dir, resource_file.url, resource_file.filename, logger)

    def _parse_xml(self, response_content):
        return EventCalendarDownloader._parse_xml_static(response_content)

    @staticmethod
    def _parse_xml_static(response_content):
        """ Sample Response
        <response>
            <version value="1.0"/>
            <channel value="NTA0Njk0NzcyNDE3NDM4NTQ1MDQ1MzAzNjg2NDgxNzMwMzk4OTI4MDQxNDA0MDk2"/>
            <pagination page="1" pagecount="1" pagesize="900" pageitems="492" items="492"
            ts="MTA5NzUzMjEwODAwMDg1NTg5NjI3OTQzNTIyMjU2MjU5MDQyMDM1NjEyMjgxMTQy"/>
            <search/>
            <results>
                <item>
                <id value="316003-1110969" type="2" deleted="0"/>
                <column name="upcoming" value="1"/>
                <column name="caption_addition" value="Kultursommer Rheinland-Pfalz im Unionsviertel Kaiserslautern"/>
                <column name="caption" value="Kultursommer Rheinland-Pfalz im Unionsviertel Kaiserslautern"/>
                <column name="icon" value="/icons/000/316/003/Logo_151104_fur_miadi_kaiserslautern_de_200x150.png"/>
                <column name="teaser" value="Erleben Sie ein abwechslungsreiches Programm mit Live-Musik ..." 2024"/>
                <column name="description" value="Der Kultursommer Rheinland-Pfalz ist eine landeseigene Stiftung.."."/>
                <column name="dstart" value="2024-04-28T00:00:00"/>
                <column name="dend" value="2024-09-22T00:00:00"/>
                <column name="created" value="21.02.2024 08:59:57"/>
                <column name="updated" value="21.02.2024 09:13:48"/>
                <column name="tags" value="Kultursommer Rheinland-Pfalz Unionsviertel Kaiserslautern"/>
                <column name="tickets" value="3"/>
                <column name="category" value="Musik"/>
                <column name="location_id" value="21097"/>
                <column name="location_name" value="Unionsviertel Kaiserslautern"/>
                <column name="location_street" value="Pirmasenser Straße"/>
                <column name="location_pobox" value="67655"/>
                <column name="location_city" value="Kaiserslautern"/>
                </item>
                ...
            </results>
        </response>
        """
        root = ET.fromstring(response_content)
        version = root.find('version').get('value')
        channel = root.find('channel').get('value')
        pagination = root.find('pagination').attrib  # currently not used
        items = []
        print("Downloaded calender version %s, channel %s" % (version, channel))
        for item in root.find('results').findall('item'):
            item_data = OrderedDict({
                'id': item.find('id').get('value'),
                'type': item.find('id').get('type'),
                'deleted': item.find('id').get('deleted'),
            })
            for col in item.findall('column'):
                item_data[col.get('name')] = col.get('value')
            item_data["dstart"] = datetime.strptime(item_data["dstart"], '%Y-%m-%dT%H:%M:%S').strftime(
                '%d.%m.%Y %H:%M:%S')
            item_data["dend"] = datetime.strptime(item_data["dend"], '%Y-%m-%dT%H:%M:%S').strftime(
                '%d.%m.%Y %H:%M:%S')
            items.append(item_data)
        return items
