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

FRONTEND_URL = "https://lautrer-wissen.de"


class FrontendURLMixin:
    def get_frontend_url(self):

        route_map = {
            "wikifishsculpture": "wiki/fish-sculptures",
            "wikifountain" : "wiki/fountains",
            "wikiculturalmonument": "wiki/cultural-monuments",
            "wikinaturalmonument": "wiki/natural-monuments",
            "wikibrewery": "wiki/breweries",
            "wikinaturalreserve" : "wiki/natural-reserves",
            "wikiritterstein" : "wiki/rittersteine",
            "wikisacralbuilding": "wiki/sacral-buildings",
            "wikistolperstein": "wiki/stolpersteine",
            'klsensorgrafanadashboard': "dashboards"
        }
        

        url_partial = route_map.get(self._meta.model_name, None)
        if url_partial is None:
            return FRONTEND_URL
        
        return f"{FRONTEND_URL}/{url_partial}/{self.pk}"

    def get_frontend_url_name(self):
        if self._meta.model_name == 'klsensorgrafanadashboard':
            return "Mehr erfahren (%s)" %(self.timefilters)
        return "Mehr erfahren"