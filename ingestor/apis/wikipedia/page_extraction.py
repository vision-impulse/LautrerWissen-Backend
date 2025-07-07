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


class WikipediaPageExtractor(object):

    def __init__(self):
        pass

    @staticmethod
    def extract_references(html_soup):
        ol_tag = html_soup.find('ol', class_="references")
        if ol_tag is None:
            return []
        references = []
        for li in ol_tag.find_all('li'):
            sup_tags = li.findAll('sup')
            if sup_tags is not None:
                for sup_tag in sup_tags:
                    sup_tag.decompose()

            reference_text, reference_url = "", ""
            reference_text = li.get_text()
            reference_text = reference_text.lstrip("↑").strip()

            li_reference = li.find(class_="reference-text")
            links = li_reference.findAll('a')
            for link in links:
                if ("class" in link.attrs and "external" in link["class"]) or "wiki" in link["href"]:
                    if not "ISBN" in link.get_text():
                        reference_text = link.get_text()
                    reference_url = link["href"]
                    if reference_url.startswith("/wiki"):
                        reference_url = "https://de.wikipedia.org" + reference_url
            references.append((reference_text, reference_url))
        return references

    @staticmethod
    def get_html_tables_for_wikipedia_page(html_soup):
        """Extract tables from parsed HTML."""
        tables = html_soup.find_all('table')
        return tables

