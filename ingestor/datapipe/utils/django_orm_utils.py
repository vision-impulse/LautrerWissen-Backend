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

import importlib
import logging

from typing import List, Dict
from shapely.wkt import dumps as shapely_to_wkt
from django.db import transaction
from django.utils.timezone import now
from django.contrib.gis.geos import GEOSGeometry
from ingestor.datapipe.utils.django_integration import setup_django
from typing import List, Dict, Callable

logger = logging.getLogger("ingestor")
setup_django()


class DjangoORMUtils:

    DJANGO_MODEL_PACKAGE = "lautrer_wissen.models"

    @staticmethod
    def get_django_model_class(model_name: str):
        """
        Dynamically imports and returns a Django model class based on the provided model name.
        """
        ext_module = importlib.import_module(DjangoORMUtils.DJANGO_MODEL_PACKAGE)
        return getattr(ext_module, model_name)

    @staticmethod
    def bulk_insert_and_cleanup(
        django_model,
        db_model_rows: List[Dict],
        modify_model_fields_func: Callable = None,
        batch_size: int = 5000,
    ):
        """
        Efficiently inserts records in bulk and removes outdated records using Django ORM.

        Steps:
        1. Assign a single insert timestamp for the operation.
        2. Bulk insert all new records with the same insert timestamp.
        3. Delete outdated records (same data_source but older insert_timestamp).
        """
        if not db_model_rows:
            return

        insert_ts = now()  # Django timezone-aware timestamp
        data_source = db_model_rows[0].get("data_source")

        # Prepare Django model instances
        model_fields = [
            field.name
            for field in django_model._meta.fields
            if field.name not in ["id", "insert_timestamp"]
        ]

        if modify_model_fields_func:
            db_model_rows = modify_model_fields_func(db_model_rows)
            logger.info(db_model_rows)

        for row in db_model_rows:
            if "geometry" in row:
                row["geometry"] = GEOSGeometry(
                    shapely_to_wkt(row["geometry"])
                )  # convert shapely object

        new_records = [
            django_model(
                **{
                    **{field: row.get(field) for field in model_fields},
                    "insert_timestamp": insert_ts,
                }
            )
            for row in db_model_rows
        ]

        # Bulk insert using Django ORM
        for i in range(0, len(new_records), batch_size):
            django_model.objects.bulk_create(
                new_records[i : i + batch_size], batch_size=batch_size
            )
            logger.info("Inserted new records...")

        # Delete outdated records
        with transaction.atomic():
            if django_model.__name__ == "GenericGeoModel":
                
                if len(new_records) > 0:
                    # Filter rows matching the data_source but with a different insert timestamp

                    queryset = django_model.objects.filter(data_source=data_source).exclude(
                        insert_timestamp=insert_ts
                    )
                    # Only keep rows of the same type as objects in the queryset
                    #types_to_delete = queryset.values_list('type', flat=True).distinct()
                    types_to_delete = [record.type for record in new_records]
                    queryset = queryset.filter(type__in=types_to_delete)
                    #queryset = queryset.filter(type__in=new_records[0]["type"])

                    deleted_count, _ = queryset.delete()
                    logger.info("Deleted %s outdated GenericGeoModel records of matching types.", deleted_count)
            else:
                # Original logic for other models
                queryset = django_model.objects.filter(data_source=data_source).exclude(
                    insert_timestamp=insert_ts
                )
                queryset |= django_model.objects.filter(data_source__isnull=True)
                queryset |= django_model.objects.filter(data_source="")
                deleted_count, _ = queryset.delete()
                logger.info("Deleted %s outdated records.", deleted_count)
        
        """
        with transaction.atomic():
            queryset = django_model.objects.filter(data_source=data_source).exclude(
                insert_timestamp=insert_ts
            )
            queryset |= django_model.objects.filter(data_source__isnull=True)
            queryset |= django_model.objects.filter(data_source="")
            deleted_count, _ = queryset.delete()
            logger.info("Deleted %s outdated records.", deleted_count)
        """