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

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from pipeline_manager.models import PipelineSchedule
from . import scheduler


@receiver(post_save, sender=PipelineSchedule)
def update_schedule(sender, instance, **kwargs):
    if not scheduler.scheduler:
        return
    scheduler.sync_schedules()


@receiver(post_delete, sender=PipelineSchedule)
def delete_schedule(sender, instance, **kwargs):
    if not scheduler.scheduler:
        return
    scheduler.sync_schedules()