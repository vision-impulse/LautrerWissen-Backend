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

from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from ingestor.datapipe.utils.django_integration import get_django_model


class PipelineType(Enum):
    KL_EVENTS = "KL_EVENTS"
    KL_EVENTS_RIS = "KL_EVENTS_RIS"
    KL_GEO_WFS = "WFS"
    KL_GEO_RESOURCES = "GEO"
    KL_SENSOR_RESOURCES = "SENSORS"
    EV_STATIONS = "EV_STATIONS"
    VRN = "VRN"
    OSM = "OSM"
    WIFI_FREIFUNK = "WIFI_FREIFUNK"
    WIFI_LOCAL = "WIFI_LOCAL"
    WIKIPEDIA = "WIKIPEDIA"
    EMERGENCY_POINTS = "EMERGENCY_POINTS"
    WGA_EVENTS = "WGA_EVENTS"
    TTN_GATEWAY = "TTN_GATEWAY"


class PipelineContext:
    """Holds information about a specific feature being processed."""

    def __init__(self, resource, out_dir, logger):
        """
        :param resource: Any resource dataclass (ResourceOSM, ResourceWFSFile, etc.)
        :param out_dir: General output directory for storing processed files
        """
        self.resource = resource  # Holds the specific resource object
        self.out_dir = out_dir  # General output directory
        self.logger = logger
        self.data_store = {}  # Dictionary to store step-specific data

    def set_data(self, key, value):
        """Store step results dynamically."""
        self.data_store[key] = value

    def get_data(self, key):
        """Retrieve step results dynamically."""
        return self.data_store.get(key)


class BasePipeline(ABC):
    """Abstract base class for pipelines."""

    def __init__(self, resources, logger, out_dir, run_record=None):
        self.resources = resources
        self.logger = logger
        self.out_dir = out_dir
        self.run_record = run_record
        self.steps = self.build_pipeline()

    @abstractmethod
    def build_pipeline(self):
        """Each pipeline must define its own steps."""
        pass

    def run(self):
        PipelineRunStep = get_django_model("PipelineRunStep")

        for resource in self.resources:
            context = PipelineContext(resource, self.out_dir, self.logger)
            self.logger.info("Processing data from: %s", context.out_dir)

            for step in self.steps:
                step_record = None
                if self.run_record and PipelineRunStep:
                    try:
                        step_record = PipelineRunStep.objects.create(
                            run=self.run_record,
                            step_name=step.__class__.__name__,
                            status="running",
                            started_at=datetime.now(),
                        )
                    except Exception as e:
                        self.logger.warning(f"Could not log step in DB: {e}")
                try:
                    success = step.execute(context)
                    if step_record:
                        step_record.status = "success" if success else "failed"
                        step_record.finished_at = datetime.now()
                        step_record.save(update_fields=["status", "finished_at"])
                    if not success:
                        self.logger.error(
                            " Stopping %s due to failure.", context.out_dir
                        )
                        # stop processing resource
                        return "error"
                except Exception as exc:
                    if step_record:
                        step_record.status = "failed"
                        step_record.message = str(exc)
                        step_record.finished_at = datetime.now()
                        step_record.save(
                            update_fields=["status", "message", "finished_at"]
                        )
                    return "error"
        return "success"
