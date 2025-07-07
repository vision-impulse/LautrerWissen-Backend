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

from enum import Enum


class WikipediaDataframeColumns(Enum):
    ADDRESS_TEXT = "loc_address_text"
    ADDRESS_LOCATION = "loc_location"
    IMAGE_URL = "image_url"
    IMAGE_FILENAME = "image_name"
    IMAGE_AUTHOR_NAME = "image_author_name"
    IMAGE_LICENSE_URL = 'image_license_url'
    IMAGE_LICENSE_TEXT = 'image_license_text'
    REFERENCE_NAMES = "reference_names"
    REFERENCE_LINKS = "reference_links"
    ADDITIONAL_IMAGE_URL_CATEGORY = "image_additional_url_category"
    ADDITIONAL_IMAGE_URLS = "image_additional_urls"
    ADDITIONAL_IMAGE_AUTHOR_NAMES = "image_additional_author_names"
    ADDITIONAL_IMAGE_LICENSE_URLS = "image_additional_license_urls"
    ADDITIONAL_IMAGE_LICENSE_TEXTS = "image_additional_license_texts"
