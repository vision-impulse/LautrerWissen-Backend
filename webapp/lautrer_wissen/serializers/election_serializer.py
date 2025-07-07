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
from ..models.elections.election_results import ElectionResult, Election


class ElectionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectionResult
        fields = ["id", "result_data", "district_type", "district_name"]


class ElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        fields = ["id", "name", "date", "data_source", "insert_timestamp", "data_acquisition_date"]


class ElectionDetailSerializer(serializers.ModelSerializer):
    results_grouped = serializers.SerializerMethodField()

    class Meta:
        model = Election
        fields = ["id", "name", "date", "data_source", "insert_timestamp", "results_grouped"]

    def get_results_grouped(self, obj):
        results = obj.results.all()
        grouped = {}
        for result in results:
            grouped.setdefault(result.district_type, []).append({
                "id": result.id,
                "result_data": result.result_data,
                "name": result.district_name
            })
        return grouped
