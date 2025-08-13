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

import traceback
import logging

from abc import ABC, abstractmethod
from datetime import datetime
from ingestor.datapipe.utils.django_orm_utils import DjangoORMUtils   

logger = logging.getLogger(__name__)

class PipelineStep(ABC):
    """Base class for pipeline steps."""

    def __init__(self, next_step=None):
        self.next_step = next_step
        
    def execute(self, ctx):
        """Each step must implement this method."""
        return False

    def handle_error(self, error, data):
        logger.error("Error in %s: %s", self.__class__.__name__, error)
        raise Exception(error)


class DefaultTransformStep(PipelineStep):

    @abstractmethod
    def transform(self, download_file, db_model, data_acquisition_date):
        pass

    def execute(self, context):
        try:
            db_model_name = context.resource.db_model_class
            db_model_class = DjangoORMUtils.get_django_model_class(db_model_name)

            data_acquisition_date = datetime.now().date()

            rows = self.transform(context, db_model_class, data_acquisition_date)
            context.set_data("rows", rows)
            return True
        except Exception as e:
            logger.error("TransformStep failed for %s, (%s)", context.resource, exc_info=True)
            raise Exception(e)
            return False