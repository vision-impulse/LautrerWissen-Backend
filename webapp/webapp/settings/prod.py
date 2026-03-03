# Copyright (c) 2026 Vision Impulse GmbH
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

from .base import *

# BB IMPORTANT: Do NOT load .env file!
# Docker or server provides real environment variables

# BB: Explicitly set to False to avoid misconfiguration!
DEBUG = False   

# Explicitly set to True to avoid misconfiguration!
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True