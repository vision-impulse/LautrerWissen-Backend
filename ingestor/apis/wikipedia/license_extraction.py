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


class WikipediaLicenseExtractor(object):

    def __init__(self):
        pass

    @staticmethod
    def short_license_from_name(full_license_name):
        short = full_license_name.replace("Creative Commons Zero", "CC0") \
            .replace("Creative Commons", "CC")\
            .replace("Attribution", "BY").replace("Share Alike", "SA")\
            .replace("Public Domain Dedication", "") \
            .replace("Public Domain", "CC0") \
            .replace("Public domain", "CC0") \
            .replace(",", "") \
            .replace("GNU Free Documentation License", "GFDL")

        return short.upper().strip()

    @staticmethod
    def extract_user_and_licence_from_image(soup):
        user, license_url, license_text = "", "", ""

        if soup.find(class_="licensetpl_link") is not None:
            license_url = soup.find(class_="licensetpl_link").get_text()
        if soup.find(class_="licensetpl_long") is not None:
            license_text = soup.find(class_="licensetpl_long").get_text()

        licensing_section = soup.find(class_="licensetpl_wrapper")
        if licensing_section is not None and license_url == "":
            links = licensing_section.findAll('a')
            for l in links:
                if 'title' in l.attrs and "creativecommons" in l["title"]:
                    license_url = l["href"]
                    license_text = l.get_text()

        author_table_row = soup.find(id="fileinfotpl_aut")
        if author_table_row is not None:
            author_td = author_table_row.find_next_sibling('td')

            for a in author_td.findAll("a"):
                if 'title' in a.attrs and 'User' in a["title"]:
                    user = a.get_text()
                    break
            if user == "":
                user = author_td.get_text()
        else:
            links = soup.findAll('a', class_="extiw")
            for link in links:
                if 'href' in link.attrs and "https://en.wikipedia.org/wiki/de:User" in link["href"]:
                    user = link.get_text()
                    break

        user = user.replace("\n", "")
        license_text = WikipediaLicenseExtractor.short_license_from_name(license_text)
        return user, license_url, license_text
