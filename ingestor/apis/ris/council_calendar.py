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

from collections import OrderedDict
import xml.etree.ElementTree as ET
from ingestor.apis import XMLDownloader
from datetime import datetime
import re


class CouncilCalendarDownloader(XMLDownloader):

    KEY_MAPPING = {
        'Gremium': 'committee',
        'Datum': 'date',
        'Zeit': 'time',
        'Ort': 'location'
    }

    def __init__(self, out_dir, resource_file, logger):
        print(resource_file)
        super(CouncilCalendarDownloader, self).__init__(out_dir, resource_file.url, resource_file.filename, logger)

    def _parse_xml(self, response_content):
        return CouncilCalendarDownloader._parse_xml_static(response_content)

    @staticmethod
    def _parse_xml_static(response_content):
        """ Sample Response
        <channel>
            <title>Ratsinformationen der Stadt Kaiserslautern</title>
            <link>https://ris.kaiserslautern.de/buergerinfo</link>
            <description>Tagesaktuelle Ratsinformationen derStadt Kaiserslautern</description>
            <language>de-de</language>
            <copyright>by Stadt Kaiserslautern</copyright>
            <item>
                <title>Sitzung: Ortsbeirat Erfenbach 05.02.2025</title>
                <description>Gremium: Ortsbeirat Erfenbach Datum: 05.02.2025 Zeit: 19:00 Uhr Ort: im Sitzungssaal der Ortsverwaltung Erfenbach, Siegelbacher Straße 95, Kaiserslautern, im Sitzungssaal der Ortsverwaltung Erfenbach, Siegelbacher Straße 95, Kaiserslautern</description>
                <link>https://ris.kaiserslautern.de/buergerinfo/rssgo.asp?si2179</link>
                <category>Sitzungen</category>
            </item>
            ...
        """
        root = ET.fromstring(response_content)
        items = []
        for item in root.find('channel').findall('item'):
            link_tag = item.find('link')
            desc = item.find('description').text
            matches = re.findall(r'(\w+):\s(.*?)(?=\s\w+:|$)', desc)

            result = dict(matches)
            result["category"] =  item.find('category').text
            result["title"] = item.find('title').text
            result["link"] = "" if link_tag is None else link_tag.text
            result = {CouncilCalendarDownloader.KEY_MAPPING.get(k, k): v for k, v in result.items()}

            items.append(result)
        return items
