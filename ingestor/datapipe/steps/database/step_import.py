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


class GenericImportStep(PipelineStep):

    def __init__(self):
        super(GenericImportStep, self).__init__()

    def execute(self, context):
        try:
            print("ImportStep...")
            db_model_name = context.resource.db_model_class
            db_model_rows = context.get_data("rows")

            print("IMPORTING DATA: ", context.resource)
            DjangoORMUtils.bulk_insert_and_cleanup(
                django_model=DjangoORMUtils.get_django_model_class(db_model_name),
                db_model_rows=db_model_rows,
                batch_size=5000
            )

            return "Success"
        except Exception as e:
            traceback.print_exc()
            print(f"Import failed for {context.resource}: {e}")
            return False