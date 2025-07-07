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

from shapely.geometry.base import BaseGeometry
from shapely.geometry import Point, LineString, Polygon


def remove_z_dimension(geometry: BaseGeometry) -> BaseGeometry:
    """
    Remove the Z dimension from a geometry if present.
    """
    if geometry is None or geometry.is_empty:
        return geometry  # Return as is if geometry is None or empty

    geom_type = geometry.geom_type
    if geom_type == 'Point':
        return Point(geometry.coords[0][:2])  # Keep only X, Y
    elif geom_type == 'LineString':
        return LineString([(x, y) for x, y, *_ in geometry.coords])
    elif geom_type == 'Polygon':
        # Remove Z from exterior and interiors
        exterior = [(x, y) for x, y, *_ in geometry.exterior.coords]
        interiors = [
            [(x, y) for x, y, *_ in interior.coords] for interior in geometry.interiors
        ]
        return Polygon(exterior, interiors)
    else:
        # Handle Multi* geometries by recursively applying to each part
        if hasattr(geometry, 'geoms'):
            return type(geometry)([remove_z_dimension(part) for part in geometry.geoms])
        return geometry  # Return as is for unsupported geometry types
