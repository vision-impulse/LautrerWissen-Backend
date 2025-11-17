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

from ingestor.datapipe.steps.base_step import PipelineStep
from ingestor.datapipe.utils.django_orm_utils import DjangoORMUtils
import traceback
import logging

logger = logging.getLogger(__name__)


from copy import deepcopy
from typing import List, Dict

def add_model_type(model_type: str):
    """
    Returns a function that will add {"type": model_type} to each row dict.
    The transformer returns a NEW list with new dicts (deepcopied).
    """
    def transform(rows: List[Dict]) -> List[Dict]:
        out = []
        for row in rows:
            r = deepcopy(row)
            r["type"] = model_type
            out.append(r)
        return out
    return transform

class DatabaseImportStep(PipelineStep):

    def __init__(self):
        super(DatabaseImportStep, self).__init__()

    def execute(self, context):
        try:
            logger.info(
                "Starting data import for model class (%s)",
                context.resource.db_model_class,
            )
            db_model_name = context.resource.db_model_class
            db_model_rows = context.get_data("rows")
            db_model_class_type = context.resource.db_model_class_type

            transform_func = None
            if db_model_class_type and db_model_name == "GenericGeoModel":
                transform_func = add_model_type(db_model_class_type)

            logger.info("Importing data: %s", context.resource)
            DjangoORMUtils.bulk_insert_and_cleanup(
                django_model=DjangoORMUtils.get_django_model_class(db_model_name),
                db_model_rows=db_model_rows,
                modify_model_fields_func=transform_func,
                batch_size=5000,
            )
            logger.info("Successfully imported data")
            return True
        except Exception as e:
            logger.error(f"Import failed for %s: %s", context.resource, exc_info=True)
            return False
